import tkinter as tk
from tkcalendar import Calendar
import requests
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv
import os

# .env 파일 활성화
load_dotenv()

API_KEY = os.getenv('API_KEY')
events = {}

def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


def get_weather(location, selected_date):
    try:
        BASE_URL = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}&units=metric&lang=kr"
        response = requests.get(BASE_URL)
        weather_data = response.json()
        for item in weather_data['list']:
            date_str = item['dt_txt'].split()[0]
            if date_str == selected_date:
                return item['weather'][0]['main'], item['main']['temp'], item['weather'][0]['icon']
        return None, None, None
    except Exception as e:
        print(f"날씨 정보를 가져오는 중 오류: {e}")
        return None, None, None


def show_weather(selected_date, location):
    description, temp, icon = get_weather(location, selected_date)
    if description and temp and icon:
        weather_label.config(text=f"{selected_date} {location} 날씨: {description}, 온도: {temp}°C")
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        icon_response = requests.get(icon_url)
        icon_data = icon_response.content
        image = Image.open(BytesIO(icon_data))
        icon_image = ImageTk.PhotoImage(image)
        weather_icon_label.config(image=icon_image)
        weather_icon_label.image = icon_image
    else:
        weather_label.config(text="날씨 정보를 불러올 수 없습니다.")
        weather_icon_label.config(image="")


def display_add_event():
    clear_right_panel()
    tk.Label(right_panel, text="제목 :").pack(pady=5)
    entry_event = tk.Entry(right_panel)
    entry_event.pack(pady=5)
    tk.Label(right_panel, text="위치 :").pack(pady=5)
    entry_location = tk.Entry(right_panel)
    entry_location.pack(pady=5)

    def save_event():
        selected_date = str(cal.selection_get())
        event_name = entry_event.get().strip()
        location = entry_location.get().strip()

        if not selected_date:
            weather_label.config(text="날짜를 선택해 주세요.")
            return
        if not event_name or not location:
            weather_label.config(text="일정 이름과 위치를 모두 입력해 주세요.")
            return

        # 날짜별 일정 리스트에 새 일정 추가
        if selected_date not in events:
            events[selected_date] = []
        events[selected_date].append({"이름": event_name, "위치": location})
        weather_label.config(text=f"{selected_date} 일정이 추가되었습니다.")
        clear_right_panel()

    tk.Button(right_panel, text="저장", command=save_event).pack(pady=10)


def display_view_event(date):
    clear_right_panel()
    tk.Label(right_panel, text=f"{date} ", font=("Pretendard", 14)).pack(pady=10)

    if date in events:
        for event_info in events[date]:
            # 박스 스타일의 프레임 추가
            event_box = tk.Frame(right_panel, bd=2, relief="groove", padx=10, pady=10, background="#7CB5C4")
            event_box.pack(pady=5, fill="x")

            # 일정 정보와 날씨 확인 버튼을 같은 행에 배치
            title_frame = tk.Frame(event_box, background="#7CB5C4")
            title_frame.pack(fill="x", pady=5)

            # 'title_frame'의 첫 번째 열 확장을 설정해 버튼이 오른쪽으로 밀리게 함
            title_frame.grid_columnconfigure(0, weight=1)

            # 일정 제목 라벨과 버튼을 같은 행에 배치
            tk.Label(title_frame, text=f"제목 : {event_info['이름']}", font=("Pretendard", 10), background="#7CB5C4").grid(
                row=0, column=0, sticky="w")

            # 날씨 확인 버튼을 오른쪽 끝에 배치
            tk.Button(title_frame, text="날씨 확인", command=lambda info=event_info: show_weather(date, info["위치"])).grid(
                row=0, column=1, sticky="e")

            # 위치 정보를 다음 행에 배치
            tk.Label(event_box, text=f"위치: {event_info['위치']}", font=("Pretendard", 10), background="#7CB5C4").pack(
                anchor="w")
    else:
        tk.Label(right_panel, text="등록된 일정이 없습니다.").pack(pady=20)


def on_date_select(event):
    selected_date = str(cal.selection_get())
    display_view_event(selected_date)


def clear_right_panel():
    for widget in right_panel.winfo_children():
        if widget != weather_label_frame:
            widget.destroy()


root = tk.Tk()
root.title("날씨 캘린더")
center_window(root, 1000, 600)

cal = Calendar(root,
               selectmode='day',
               font=("Pretendard", 9),
               background='light blue',
               foreground='black',
               selectbackground='dark blue',
               selectforeground='white',
               normalbackground='white',
               weekendbackground='light gray',
               weekendforeground='black',
               othermonthbackground='light gray',
               othermonthforeground='dark gray',
               othermonthwebackground='gray',
               othermonthweforeground='black',
               todaybackground='orange',
               todayforeground='black'
               )

cal.place(x=20, y=30, width=500, height=500)

add_event_button = tk.Button(root, text="일정 추가", command=display_add_event,anchor="center")
add_event_button.place(x=680, y=30, width=80, height=30)

right_panel = tk.Frame(root, width=250, height=500)
right_panel.place(x=620, y=60)

# weather_label을 중앙에 배치할 Frame 생성
weather_label_frame = tk.Frame(right_panel)
weather_label_frame.pack(expand=True)  # expand를 통해 빈 공간에 중앙 배치

weather_label = tk.Label(weather_label_frame, text="날짜를 선택해주세요.", font=("Pretendard", 14))
weather_label.pack(pady=10)

weather_icon_label = tk.Label(weather_label_frame)
weather_icon_label.pack(pady=10)

cal.bind("<<CalendarSelected>>", on_date_select)

root.mainloop()