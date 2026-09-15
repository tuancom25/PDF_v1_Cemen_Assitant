
hãy nhớ lại về chương trình  "AI trợ lý lý kỹ thuật với 20 books pdf -> 500 book pdf "
CHúng ta đang xây build, đang  đến đoạn xây dựng pipe line - khung luồng chính của  chương trình 
với sẽ cần 2 vòng lăp qua document và page ( hoặc contentBlock) .  

Tôi đang được gợi ý tên file chính là "document_pipeline.py"  cũng hay nhưng tôi đang đặt tạm là 
p_main_0.py 
và 
p_main_1.py. p_main_0.py  để viết luồng chính vào  và file kia là để hỗ trở sửa code, test . 

luồng chính  đang đi đã qua đoạn group,  đến đoạn simantec , nhưng còn  phần  unassined đã ổn chưa 
hay check lại để đến tiếp đoạn semantic,  rồi đến chunking 

Tiếp tục chuẩn hoá luồng khung chương trình chính,  với các gợi ý vừa như là 
" Một điều nữa: đừng để Pipeline biết chi tiết thuật toán"
rồi để tôi đặt nó vào  file p_main_0.py  


#---------------------------------------------

6. Semantic mới là nơi xác định "nó là gì"

Đây là ranh giới chúng ta đã thống nhất.

Group

Trả lời:

"Block này thuộc vùng/cấu trúc nào?"

Ví dụ:

Group 0
Group 1
Group 2
UnassignedGroup 0
Semantic

Trả lời:

"Nội dung này đóng vai trò gì?"

Ví dụ:

HEADING
PARAGRAPH
TABLE
CAPTION
FIGURE
LIST
FOOTNOTE
