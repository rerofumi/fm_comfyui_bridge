import json
import importlib.resources

class WorkflowTemplate:
    def __init__(self, workflow_file_name: str):
        self.workflow_file_path = workflow_file_name
        # Allow loading from a specific package an module, defaulting to "fm_comfyui_bridge.Workflow"
        # This is to make the class more reusable and testable.
        package_name, *resource_name_parts = workflow_file_name.split('.')
        if not resource_name_parts: # if no dot, it's just a filename
            resource_name = workflow_file_name
            package_name = "fm_comfyui_bridge.Workflow"
        else:
            # reconstruct the resource name if it contained dots
            resource_name = '.'.join(resource_name_parts)


        try:
            with importlib.resources.open_text(package_name, resource_name) as f:
                self.workflow = json.load(f)
        except FileNotFoundError:
            # Fallback for testing or direct path usage if not found as resource
            try:
                with open(workflow_file_name, 'r') as f:
                    self.workflow = json.load(f)
            except FileNotFoundError:
                raise ValueError(f"Workflow file '{workflow_file_name}' not found either as a resource in '{package_name}' or as a direct file path.")


    def _find_node_id_by_title(self, title: str) -> str:
        for node_id, node_info in self.workflow.items():
            if node_info.get("_meta", {}).get("title") == title:
                return node_id
        raise ValueError(f"Node with title '{title}' not found.")

    def set_input_by_title(self, title: str, input_name: str, value: any):
        node_id = self._find_node_id_by_title(title)
        if node_id not in self.workflow:
            raise ValueError(f"Node with ID '{node_id}' (found by title '{title}') not in workflow. This should not happen.")
        if "inputs" not in self.workflow[node_id]:
             self.workflow[node_id]["inputs"] = {} # Ensure 'inputs' key exists
        if input_name not in self.workflow[node_id]["inputs"]:
            # Optional: Raise error only if input_name is critical or not meant to be created.
            # For flexibility, we can allow creating the input if it doesn't exist.
            # raise ValueError(f"Input '{input_name}' not found in node with title '{title}' (ID: {node_id}). Available inputs: {list(self.workflow[node_id]['inputs'].keys())}")
            pass # Allow creating new input if it doesn't exist
        self.workflow[node_id]["inputs"][input_name] = value

    def get_workflow(self) -> dict:
        return self.workflow

    def _get_new_node_num(self) -> int:
        node_num = 0
        for node_id_str in self.workflow.keys():
            try:
                num = int(node_id_str)
                if num > node_num:
                    node_num = num
            except ValueError:
                # Handle cases where node_id might not be a simple integer string
                pass # Or log a warning, or adopt a more robust ID generation
        return node_num + 1

    def _replace_value_recursive(self, data, old_value_tuple, new_value_tuple):
        # old_value_tuple is (old_node_id_str, link_index) e.g. ("4", 0)
        # new_value_tuple is (new_node_id_str, link_index) e.g. ("100", 0)
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 2 and \
                   str(value[0]) == str(old_value_tuple[0]) and value[1] == old_value_tuple[1]:
                    new_dict[key] = [new_value_tuple[0], new_value_tuple[1]]
                elif isinstance(value, (dict, list)):
                    new_dict[key] = self._replace_value_recursive(value, old_value_tuple, new_value_tuple)
                else:
                    new_dict[key] = value
            return new_dict
        elif isinstance(data, list):
            # Check if the list itself is the old_value_tuple (direct match for a link)
            if len(data) == 2 and str(data[0]) == str(old_value_tuple[0]) and data[1] == old_value_tuple[1]:
                return [new_value_tuple[0], new_value_tuple[1]]

            new_list = []
            for item in data:
                # Check if item is a list representing a link e.g. ["node_id", output_idx]
                if isinstance(item, list) and len(item) == 2 and \
                   str(item[0]) == str(old_value_tuple[0]) and item[1] == old_value_tuple[1]:
                    new_list.append([new_value_tuple[0], new_value_tuple[1]])
                elif isinstance(item, (dict, list)):
                    new_list.append(self._replace_value_recursive(item, old_value_tuple, new_value_tuple))
                else:
                    # Otherwise, just append the item as is
                    new_list.append(item)
            return new_list
        else:
            return data

    def insert_loras(self, lora, checkpoint_title: str):
        # Find the checkpoint node ID using its title
        # This is the initial node providing model and clip outputs.
        source_node_id_for_chaining = self._find_node_id_by_title(checkpoint_title)

        lora_num = lora.lora_num # Assuming SdLoraYaml has .lora_num
        for i in range(lora_num):
            if lora.lora_enabled_flag(i): # Assuming SdLoraYaml has .lora_enabled_flag(i)
                new_lora_node_id = str(self._get_new_node_num())

                # Define the new LoRA Loader node
                self.workflow[new_lora_node_id] = {
                    "inputs": {
                        "lora_name": lora.lora_model(i), # Assuming SdLoraYaml has .lora_model(i)
                        "strength_model": lora.lora_strength(i), # Assuming SdLoraYaml has .lora_strength(i)
                        "strength_clip": lora.lora_strength(i),
                        "model": [source_node_id_for_chaining, 0], # Connect to previous node in chain (model)
                        "clip": [source_node_id_for_chaining, 1],  # Connect to previous node in chain (clip)
                    },
                    "class_type": "LoraLoader",
                    "_meta": {"title": f"Load LoRA: {lora.lora_model(i)} (Chain {i+1})"},
                }

                # Now, update all other nodes in the workflow that were previously connected to
                # `source_node_id_for_chaining` to instead connect to `new_lora_node_id`.
                temp_workflow_after_rewire = {}
                for existing_node_id, existing_node_info in self.workflow.items():
                    if existing_node_id == new_lora_node_id:
                        temp_workflow_after_rewire[existing_node_id] = existing_node_info
                        continue

                    updated_node_info_model = self._replace_value_recursive(existing_node_info,
                                                                        (source_node_id_for_chaining, 0),
                                                                        (new_lora_node_id, 0))
                    updated_node_info_final = self._replace_value_recursive(updated_node_info_model,
                                                                        (source_node_id_for_chaining, 1),
                                                                        (new_lora_node_id, 1))
                    temp_workflow_after_rewire[existing_node_id] = updated_node_info_final

                self.workflow = temp_workflow_after_rewire

                # For the next LoRA in the chain (if any), it should connect to the LoRA we just added.
                source_node_id_for_chaining = new_lora_node_id

                # After adding a LoRA and rewiring, it's possible the new LoRA node itself
                # (new_lora_node_id) might have had its own model/clip inputs rewired if they
                # were initially pointing to source_node_id_for_chaining (which they were by definition).
                # We need to ensure they are correctly pointing to the *original* source_node_id_for_chaining
                # *before* this LoRA was added, or rather, the output of the *previous* LoRA in the chain.
                # The current logic: new LoRA connects to `source_node_id_for_chaining`.
                # Then everything that pointed to `source_node_id_for_chaining` now points to new LoRA.
                # Then `source_node_id_for_chaining` becomes the new LoRA for the next iteration. This is correct.
                # One small detail: the `_get_new_node_num()` will increment each time, ensuring unique IDs.
                # The title of the LoRA node also gets the chain number.

    # Example of how to get specific output node (e.g. for final image)
    def get_output_node_id_by_class_type(self, class_type: str) -> str | None:
        for node_id, node_info in self.workflow.items():
            if node_info.get("class_type") == class_type:
                return node_id
        # Fallback or more specific search might be needed if multiple nodes of same type
        # For "Save Image" it's usually unique enough
        # For others, title based search might be better if class_type is too generic
        if class_type == "SaveImage": # Common one
             for node_id, node_info in self.workflow.items():
                if node_info.get("_meta", {}).get("title") == "Save Image":
                    return node_id
        return None # Or raise error
