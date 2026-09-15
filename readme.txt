python scripts/analyze_pdfs.py --input data/raw --recursive

Nó có nghĩa:

"Hãy tìm tất cả PDF trong data/raw và phân tích cấu trúc PDF bằng PyMuPDF."

Ví dụ:

data/raw/
├── book01.pdf
├── book02.pdf
├── book03.pdf
...
└── book20.pdf

python scripts/analyze_pdfs.py --input data/raw --recursive

sẽ xử lý:

book01.pdf
book02.pdf
book03.pdf
...
book20.pdf
Nó làm gì?

Nó làm gì?

Ví dụ book01.pdf có 500 trang.

Analyzer sẽ kiểm tra từng trang:

Page 1
    có text?
    có image?
    có vector?
    bao nhiêu text block?

Page 2
    có text?
    có image?
    ...

...

Page 500

Sau đó tạo:

data/processed/documents/book01/

và:

manifest.json
pages/
text/
figures/
Đây là bước tôi muốn bạn chạy đầu tiên.

Chưa OCR.

manifest.json
pages/
text/
figures/
Mục đích là trả lời câu hỏi:

20 cuốn PDF của tôi thực chất có cấu trúc như thế nào?

========== Lệnh 2 =============
4. Lệnh 2 — thêm OCR

Sau khi chạy bước 1, bạn chạy:

python scripts/analyze_pdfs.py --input data/raw --recursive --ocr

Điểm quan trọng:

Đây vẫn là cùng một chương trình.

Chỉ thêm:

--ocr

Nghĩa là:

"Ngoài phân tích PDF, nếu gặp trang có ít/không có text layer và có dấu hiệu là scan, hãy render trang rồi chạy PaddleOCR."

Ví dụ:

book01.pdf

Page 1    → text PDF → không cần OCR
Page 2    → text PDF → không cần OCR
Page 3    → scan     → OCR
Page 4    → scan     → OCR
Page 5    → text PDF → không cần OCR

Kết quả:

text/
    page_0001.txt
    page_0002.txt
    page_0005.txt

ocr/
    page_0003.json
    page_0004.json

Đây chính là lý do tôi muốn chạy bước 1 trước.

Bạn sẽ biết:

20 cuốn
↓
bao nhiêu trang là PDF text?
bao nhiêu trang là scan?

rồi mới biết OCR cần thiết đến mức nào.

========= lệnh 3 ======================
5. Lệnh 3 — thêm LayoutParser
python scripts/analyze_pdfs.py --input data/raw --recursive --ocr --layout

Lần này chúng ta bật thêm:

--layout

Nó có nghĩa:

"Hãy dùng mô hình computer vision để phân tích bố cục trang."

Ví dụ một trang:

┌──────────────────────────────┐
│          TITLE               │
│                              │
│ ┌──────────┐  ┌───────────┐ │
│ │ TEXT     │  │ TEXT      │ │
│ │          │  │           │ │
│ └──────────┘  └───────────┘ │
│                              │
│       ┌──────────────┐       │
│       │   FIGURE     │       │
│       └──────────────┘       │
│                              │
│       TABLE                  │
└──────────────────────────────┘

LayoutParser cố gắng nhận diện:

Title
Text
Table
Figure
List

Vì vậy:

--ocr

và

--layout

là hai khả năng khác nhau.


3. Nhưng hiện tại CLI của bạn đã có --resume chưa?

Đây mới là thứ tôi muốn bạn kiểm tra.

Trước đó --help của bạn cho:

usage: analyze_pdfs.py [-h] --input INPUT [--recursive] [--ocr] [--layout] [--dpi DPI]

Không thấy:

--resume
--force

Trong khi BatchAnalyzer.run() đã có:

resume=False,
force=False

Nếu scripts/analyze_pdfs.py chưa truyền hai option này thì tính năng resume ở BatchAnalyzer chưa sử dụng được từ command line.

Tôi khuyên thêm:

--resume
--force

Sau đó có thể có 3 cách chạy:

Chạy bình thường từ đầu
python -m scripts.analyze_pdfs --input data/raw --ocr --layout
Tiếp tục từ checkpoint
python -m scripts.analyze_pdfs --input data/raw --ocr --layout --resume
Ép chạy lại
python -m scripts.analyze_pdfs --input data/raw --ocr --layout --resume --force
python -m scripts.test_loader