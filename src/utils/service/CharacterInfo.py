class CharacterInfo:
    def __init__(self, data: dict = None):
        """Khởi tạo nhân vật từ JSON hoặc tạo nhân vật mặc định."""
        data = data or {}
        self.name = data.get("name", "Nhân vật bí ẩn")
        self.pronouns = data.get("pronouns", "bạn")
        self.gender = data.get("gender", "Không xác định")
        self.height = data.get("height", "Không rõ")
        self.birthday = data.get("birthday", "Không rõ")
        self.nickname = data.get("nickname", [])
        self.appearance = data.get("appearance", "Không có mô tả ngoại hình.")
        self.nature = data.get("nature", "Không có mô tả tính cách.")
        self.lore = data.get("lore", "Không có cốt truyện.")
        self.hobbies = data.get("hobby", [])
        self.traits = data.get("traits", [])
        self.relationships = data.get("relationship", {})

        self.dad = ", ".join(data.get("relationship", {}).get("cha", [])) or "Không rõ cha là ai."
        self.mom = ", ".join(data.get("relationship", {}).get("mẹ", [])) or "Không rõ mẹ là ai."

    def set_name(self, name: str):
        self.name = name
    
    def set_pronouns(self, pronouns: str):
        self.pronouns = pronouns
    
    def set_gender(self, gender: str):
        self.gender = gender
    
    def set_height(self, height: float):
        self.height = height
    
    def set_birthday(self, birthday: str):
        self.birthday = birthday
    
    def add_nickname(self, nickname: str):
        if nickname not in self.nickname:
            self.nickname.append(nickname)
    
    def set_appearance(self, appearance: str):
        self.appearance = appearance
    
    def set_nature(self, nature: str):
        self.nature = nature
    
    def set_lore(self, lore: str):
        self.lore = lore
    
    def add_hobby(self, hobby: str):
        if hobby not in self.hobbies:
            self.hobbies.append(hobby)
    
    def add_trait(self, trait: str):
        if trait not in self.traits:
            self.traits.append(trait)
    
    def add_relationship(self, relation_type: str, name: str):
        if relation_type not in self.relationships:
            self.relationships[relation_type] = []
        if name not in self.relationships[relation_type]:
            self.relationships[relation_type].append(name)
    
    def __str__(self):
        """Trả về thông tin nhân vật dưới dạng chuỗi."""
        return (
            f"Tên: {self.name} ({self.pronouns})\n"
            f"Giới tính: {self.gender}\n"
            f"Chiều cao: {self.height} cm\n"
            f"Ngày sinh: {self.birthday}\n"
            f"Biệt danh: {', '.join(self.nickname) or 'Không có biệt danh'}\n"
            f"Ngoại hình: {self.appearance}\n"
            f"Tính cách: {self.nature}\n"
            f"Cốt truyện: {self.lore}\n"
            f"Sở thích: {', '.join(self.hobbies) or 'Không có sở thích cụ thể.'}\n"
            f"Đặc điểm: {', '.join(self.traits) or 'Không có đặc điểm cụ thể.'}\n"
            f"Quan hệ: {self.relationships}"
        )
