import json

class FileWorker:
    def __init__(self):
        self.personality_path = 'resources/personality/personality.jsonl'

    def get_details(self, character_id):
        try:
            with open(self.personality_path, 'r', encoding='utf-8') as file:
                for line in file:
                    data = json.loads(line.strip())
                    if character_id in data:
                        return data[character_id][0]
            return None

        except (json.JSONDecodeError, KeyError) as e:
            return None
        
    def new_details(self, user_name, user_global_name):
        new_data = {
            user_name: [
                {
                    "name": user_global_name,
                    "pronouns": "bạn",
                    "gender": "",
                    "height": "",
                    "birthday": "",
                    "nickname": [],
                    "relationship": {},
                    "appearance": "",
                    "nature": "",
                    "lore": "",
                    "hobby": [],
                    "traits": []
                }
            ]
        }

        try:
            with open(self.personality_path, 'a', encoding='utf-8') as file:
                json.dump(new_data, file, ensure_ascii=False)
                file.write('\n')

        except Exception as e:
            print(f"Error occurred: {e}")
            return False

        return True

