# Tên Game: RushRelic

> Một trò chơi giải đố đơn giản dựa trên trò chơi "Rush Hour", sử dụng thuật toán DFS, BFS, A\*, UCS để tìm đường đi cho xe thoát ra khỏi bãi đỗ.

---

## 👥 Thành viên nhóm

| Họ và tên       | Vai trò                                                       |
| --------------- | ------------------------------------------------------------- |
| Trần Hải Đức    | Trưởng nhóm, thiết kế hệ thống và quản lý công việc           |
| Huỳnh Minh Đoàn | Thiết kế giao diện và UX/UI                                   |
| Trần Thái Bảo   | Đánh giá và so sánh các thuật toán, quản lý hiệu ứng âm thanh |
| Trần Sở Vinh    | Lập trình các thuật toán giải BFS, DFS, A\*, UCS              |

---

## Demo

![Gameplay](./code/Map/Map10.png)

---

## Tính năng chính

- Bản đồ 6x6 mô phỏng bãi đậu xe.
- Nhiều loại xe: xe ngang, xe dọc, xe cần giải.
- Giao diện trực quan với Pygame.
- Giải tự động bằng thuật toán DFS, BFS, A\*, UCS.
- Hiển thị số bước di chuyển, cũng như các giá trị tính toán.

---

## Cài đặt

1. **Clone repo:**

   ```bash
   git clone https://github.com/ban/rush-hour-game.git .
   ```

2. **Cài đặt thư viện:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy game:**

   ```bash
   python code/main.py
   ```

## Luật chơi

- **Mục tiêu**: Di chuyển các xe khác để tạo đường cho xe đỏ thoát khỏi bãi.
- **Cách chơi**:
  - Click vào xe để chọn.
  - Dùng các phím mũi tên hoặc thao tác chuột để di chuyển.
  - Có thể chọn “Tự động giải” nếu muốn xem lời giải.

---

## Ghi chú

- Dự án này được tạo với mục đích học thuật.
- Có thể mở rộng thêm các thuật toán như IDA\*, Greedy, v.v.

---

## Kế hoạch tương lai

- [ ] Thêm nhiều màn chơi
- [ ] Thêm chế độ người chơi tự tạo map
- [ ] Tích hợp leaderboard online
- [ ] Giao diện đẹp hơn với hiệu ứng animation

---
