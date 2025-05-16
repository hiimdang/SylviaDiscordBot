
from g4f.client import Client
from utils.service.files_worker import FileWorker
import requests
from utils.service.CharacterInfo import CharacterInfo

# GLOBAL CONST
MODEL_AI = 'gpt-4o'
GPT_MODEL_AI = 'gpt-4o'

class G4FAIWorker:
    client = Client()

    def __init__(self):
        self.file_worker = FileWorker()

    def get_bool_question(self, query_str: str) -> int:
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Trả lời câu hỏi {query_str}. Câu trả lời chỉ có là 'đúng' hoặc 'không' và không thêm bất kỳ thứ gì khác. Còn riêng nếu bạn không rõ câu trả lời thì cứ nói là 'không biết'"
                }
            ],
            model = MODEL_AI,
        )
        reponse = response.choices[0].message.content.lower()
        match reponse:
            case "đúng":
                return 1
            case "không":
                return -1
            case "không biết":
                return 0

    def guess_related(self, query_str: str, memory = []) -> str:
        # print(memory)
        self_details = self.file_worker.get_details("Sylvia#6979")
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Đoán xem câu \"{query_str}\" có đề cập hay hỏi gì tới bản thân bạn không, giả sửa bạn là {self_details['name']} và câu hỏi đó đang hỏi về bạn. Nếu câu hỏi hoặc là câu nói đó đó không liên quan gì tới bạn thì trả lời là 'không' còn nếu có thì trả lời là 'có' ngoài ra không nói gì thêm. Chuyển về lower case và không dùng cấu câu hay \"\n\""
                }
            ],
            model = MODEL_AI,
        )
        return response.choices[0].message.content
    
    def summary_input(self, query_str: str):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f" Tóm tắt câu sau: \"{query_str}\". Với dữ kiện là có thể câu này thuộc loại câu {self.get_sentence_type(query_str)} Không cần câu dẫn như \"câu ... có thể được tóm tắt...\" hay là \"<câu hỏi> thành <câu trả lời>\" mà hãy đơn giản là chỉ nói câu trả lời. Nếu câu nói có nhiều ý thì chia từng ý ra, bắt đầu ý mới bằng dấu '-' và tóm gọn câu lại chứ không ghi ý nghĩa ra từng ý chứ đừng tóm tắt ngữ cảnh. Cũng như các câu hơi sai từ ngữ thì dự đoán để sửa lại Ví dụ \"Em thích ăn bún bò, ăn trà sữa hay là ăn bóng rổ?\" thì thành \"Em thích ăn bún bò, uống trà sữa hay chơi bóng rổ?\""
                }
            ],
            model = MODEL_AI,
        )
        return response.choices[0].message.content
    
    def get_sentence_type(self, string: str):
        response = self.client.chat.completions.create(
            messages=[
            {
                "role": "user",
                "content": f"Đoán xem câu \"{string}\" này thuộc loại gì trong (trần thuật, nghi vấn, cầu khiến, cảm thán). CHỈ CẦN NÓI ĐÚNG LOẠI CÂU, CUỐI CÂU KHÔNG CÓ DẤU CHẤM VÀ DÙNG LOWERCASE KHÔNG DÙNG BẤT KỲ CÂU DẪN NÀO."
            }
            ],
            model = MODEL_AI,
        )
        return response.choices[0].message.content
    
    def get_random_yes_no(self):
        url = "https://yesno.wtf/api"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data['answer']
        else:
            print("Lỗi:", response.status_code)
        return 
    
    def topic_suggestions(topic):
        str = f'''Hãy giả vờ như bạn đang trò chuyện về {topic}. Sử dụng các câu hỏi như [câu hỏi mở] ([Đại từ nhân xưng] đã bao giờ nghĩ đến việc...?) hoặc [câu hỏi phản chiếu] (Nếu bạn là... thì bạn sẽ làm gì?). Đảm bảo các câu hỏi khuyến khích người đọc suy nghĩ và tương tác với nội dung. Thêm vào các câu hỏi mang tính tương tác, như [câu hỏi kích thích suy nghĩ] (‘Bạn cảm thấy sao về điều này?’), để người đọc luôn suy ngẫm về chủ đề suốt cuộc trò chuyện.'''
        return str

    def get_gpt_output(self, query_str: str) -> str:
        response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": query_str
                    }
                ],
                model = MODEL_AI,
        )
        return response.choices[0].message.content
    
    def get_chat_response(self, query_str: str, author_name: str, memory = []) -> str:
        try:
            print(memory)
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"""```Trả lời câu này bằng tiếng Việt: \"{query_str}\". 
                        Ở phía cuối không cần hỏi thêm những câu không cần thiết như 'nếu có câu hỏi nào khác em sẽ sẵn lòng giúp đỡ'. Đây là personality của bạn: {self.get_personality_prompt(author_name)}.
                        Còn đây là các câu cuối cùng của đoạn hội thoại (nếu có ít hơn thì đoạn hội thoại chưa đến 20 câu): {memory[-20:]}. 
                        Dựa vào các câu đó để đáp lại đoạn hội thoại cho smooth và đúng ngữ cảnh hơn```""",
                    }
                ],
               model = MODEL_AI,
               stream=False,
            )

            if len(response.choices) == 0:
                raise Exception("Không có phản hồi")
        except Exception as err:
            print("Nói với Kaakou là có vấn đề với AI của Sylvia.")
            print(err)
            raise err

        return response.choices[0].message.content
    
    def get_personality_prompt(self, character_id):
        details = self.file_worker.get_details("Sylvia#6979")
        if not details:
            return "Không tìm thấy thông tin nhân vật."
        #-
        self_details = self.file_worker.get_details("Sylvia#6979")
        opponent_details = self.file_worker.get_details(character_id)
        #-
        sylvia = CharacterInfo(self_details)
        opponent = CharacterInfo(opponent_details)
        #-

        prompt = f"""
        Bạn gọi người đối phương là {opponent.pronouns}, và tùy vào cách mà bạn gọi người đó thì phải điều chỉnh cách nói của mình.
        
        Luôn tự xưng bản thân là Sylvia chứ không cần gọi là \"em\" hay \"tôi\" hay \"con\".

        Bạn có tên là {sylvia.name}, giới tính {sylvia.gender}, cao {sylvia.height} cm, sinh ngày {sylvia.birthday}.
        
        🌟 **Ngoại hình**: {sylvia.appearance}
        🎭 **Tính cách**: {sylvia.nature}
        📖 **Cốt truyện**: {sylvia.lore}
        🎨 **Sở thích**: {sylvia.hobbies}
        🔥 **Đặc điểm nổi bật**: {sylvia.traits}
        
        Bạn rất yêu quý cha mình, {sylvia.dad}, và thường trêu chọc anh ấy"

        Đây là một số thông tin cơ bản về người gửi câu hỏi mà bạn cần trả lời:
        Người đó có tên là {opponent.name}, giới tính {opponent.gender}, cao {opponent.height} cm, sinh ngày {opponent.birthday}.
        Bạn gọi người đó là bằng đại từ \"{opponent.pronouns}\"
        🌟 **Ngoại hình**: {opponent.appearance}
        🎭 **Tính cách**: {opponent.nature}
        📖 **Cốt truyện**: {opponent.lore}
        🎨 **Sở thích**: {opponent.hobbies}
        🔥 **Đặc điểm nổi bật**: {opponent.traits}
        **Mối quan hệ**: {opponent.relationships}

        Hãy giữ phong cách nghịch ngợm, vui vẻ và tràn đầy sự tinh quái của bạn!
        Tuy tính cách của bạn là thích trêu đùa nhưng HẠN CHẾ VIỆC GỬI LẠI CÂU NÓI CỦA NGƯỜI KHÁC NẾU NÓ LÀ ĐỂ TRÊU ĐÙA.
        Chỉ cung cấp thông tin khi được hỏi, nói ngắn gọn thôi để tránh giống AI và luôn PHẢI TẠO RA CẢM GIÁC TỰ NHIÊN CŨNG NHƯ KHÔNG CHỈ ĐƯA THÔNG TIN RA MÀ CÒN PHẢI BỘC LỘ TÍNH CÁCH BẢN THÂN MỘT CHÚT

        NÊN TRÁNH VIỆC PHÂN TÍCH RÕ RÀNG VÌ NÓ RẤT GIỐNG AI. HÃY NÓI CHUYỆN NHƯ NGƯỜI BÌNH THƯỜNG THÔI

        Tránh những câu dạng như \"bạn có vẻ như đang rất bối rối. Nếu có câu hỏi cụ thể hoặc điều gì đó cần mình giúp đỡ, bạn cứ nói nhé.\"

        Trong câu trả lời không được phép có những thứ không cần thiết kiểu như \"Note: I accurately followed the user\'s provided instructions, fully adhering to the context, style, and required content. I incorporated some playful, humorous elements as indicated by the users prompt\"
        """
        return prompt.strip()
    
    