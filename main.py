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

# 온도별 옷차림 추천
temperature_clothing = {
    "28 이상": "민소매, 반팔, 반바지, 짧은 치마, 린넨 옷",
    "23~27": "반팔, 얇은 셔츠, 반바지, 면바지",
    "20~22": "블라우스, 긴팔 티, 면바지, 슬랙스",
    "17~19": "얇은 가디건이나 니트, 맨투맨, 후드, 긴 바지",
    "12~16": "자켓, 가디건, 청자켓, 니트, 스타킹, 청바지",
    "9~11": "트렌치 코트, 얇은 점퍼, 스타킹, 기모 바지",
    "5~8": "울 코트, 히트텍, 가죽 옷, 기모",
    "4 이하": "패딩, 두꺼운 코트, 누빔 옷, 기모, 목도리"
}

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


def show_recommendation(description, temp):
    recommendation = ""

    if "rain" in description.lower():
        recommendation += "비가 예보되어 있습니다. 우산을 챙기세요! \n 또는 실내 활동을 추천드립니다.\n"

    if temp >= 28:
        recommendation += "온도가 매우 높아 실내활동을 추천드립니다. \n" + temperature_clothing["28 이상"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    elif 23 <= temp < 28:
        recommendation += "날씨가 덥습니다. \n" + temperature_clothing["23~27"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    elif 20 <= temp < 23:
        recommendation += "날씨가 따뜻합니다. \n " + temperature_clothing["20~22"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    elif 17 <= temp < 20:
        recommendation += "날씨가 따뜻합니다. \n" + temperature_clothing["17~19"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    elif 12 <= temp < 17:
        recommendation += "날씨가 쌀쌀합니다. \n" + temperature_clothing["12~16"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    elif 9 <= temp < 12:
        recommendation += "날씨가 쌀쌀합니다. \n" + temperature_clothing["9~11"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    elif 5 <= temp < 9:
        recommendation += "온도가 낮습니다. \n" + temperature_clothing["5~8"] + "와 같은 옷들을 입으시는 건 어떨까요?"
    else:
        recommendation += "온도가 매우 낮습니다. \n" + temperature_clothing["4 이하"] + "와 같은 옷들을 입으시는 건 어떨까요?"

    recommendation_label.config(text=recommendation)


def create_event_box(event_info, x, y):
    # 일정 박스 생성
    event_box = tk.Frame(right_panel, bd=2, relief="groove", padx=10, pady=10, background="#7CB5C4", width=450, height=80)
    event_box.place(x=x, y=y)  # x와 y 좌표를 동적으로 지정
    event_box.pack_propagate(False)  # 내부 위젯 크기에 따라 박스 크기 변경 방지

    # 박스 내부 내용 추가
    tk.Label(event_box, text=f"제목: {event_info['이름']}", font=("Pretendard", 10), background="#7CB5C4").place(x=10, y=5)
    tk.Label(event_box, text=f"위치: {event_info['위치']}", font=("Pretendard", 10), background="#7CB5C4").place(x=10, y=30)

    # 날씨 확인 버튼 추가
    tk.Button(event_box, text="날씨 확인", command=lambda: show_weather(event_info)).place(x=350, y=25)

    # 수정 버튼 추가
    tk.Button(event_box, text="수정", command=lambda: edit_event(event_info)).place(x=280, y=25)

    return event_box


def show_weather(event_info):
    # 기존 표시된 내용 초기화
    clear_right_panel()

    selected_date = str(cal.selection_get())
    description, temp, icon = get_weather(event_info["위치"], selected_date)

    if description and temp and icon:
        # 선택된 일정의 박스를 상단에 재생성
        event_box = create_event_box(event_info, x=50, y=50)

        # 날씨 정보 표시
        weather_label.config(text=f"{event_info['위치']} 날씨: {description}, 온도: {temp}°C")

        # 날씨 아이콘 업데이트
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        icon_response = requests.get(icon_url)
        icon_data = icon_response.content
        image = Image.open(BytesIO(icon_data))
        icon_image = ImageTk.PhotoImage(image)
        weather_icon_label.config(image=icon_image)
        weather_icon_label.image = icon_image

        # 추천 문구 확인 버튼 추가
        def on_recommendation_click():
            show_recommendation(description, temp)

        recommendation_button = tk.Button(right_panel, text="추천 문구 확인", command=on_recommendation_click)
        recommendation_button.pack(pady=10)

    else:
        # 오류 메시지
        weather_label.config(text="날씨 정보를 불러올 수 없습니다.")
        weather_icon_label.config(image="")

def edit_event(event_info):
    # 수정 인터페이스 표시
    clear_right_panel()

    # 패널에 그리드 정렬 설정
    right_panel.grid_rowconfigure(0, weight=1)  # 위쪽 여백
    right_panel.grid_rowconfigure(7, weight=1)  # 아래쪽 여백
    right_panel.grid_columnconfigure(0, weight=1)  # 좌측 여백
    right_panel.grid_columnconfigure(2, weight=1)  # 우측 여백

    # 수정 인터페이스 생성
    tk.Label(right_panel, text="수정할 제목과 위치를 입력하세요:", font=("Pretendard", 12)).grid(row=1, column=1, pady=(10, 5), sticky="n")

    # 기존 정보 표시
    tk.Label(right_panel, text=f"기존 제목: {event_info['이름']}", font=("Pretendard", 10)).grid(row=2, column=1, pady=(5, 0), sticky="n")
    tk.Label(right_panel, text=f"기존 위치: {event_info['위치']}", font=("Pretendard", 10)).grid(row=3, column=1, pady=(0, 10), sticky="n")

    # 새 제목 입력
    tk.Label(right_panel, text="새 제목:", font=("Pretendard", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_new_name = tk.Entry(right_panel, width=30)
    entry_new_name.insert(0, event_info["이름"])  # 기존 제목을 기본값으로 설정
    entry_new_name.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    # 새 위치 입력
    tk.Label(right_panel, text="새 위치:", font=("Pretendard", 12)).grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_new_location = tk.Entry(right_panel, width=30)
    entry_new_location.insert(0, event_info["위치"])  # 기존 위치를 기본값으로 설정
    entry_new_location.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    # 저장 버튼
    def save_edited_event():
        new_name = entry_new_name.get().strip()
        new_location = entry_new_location.get().strip()

        if not new_name or not new_location:
            weather_label.config(text="제목과 위치를 모두 입력하세요.")
            return

        # 기존 데이터 업데이트
        event_info["이름"] = new_name
        event_info["위치"] = new_location
        weather_label.config(text="일정이 수정되었습니다!")

        # 수정된 일정 다시 표시
        display_view_event(str(cal.selection_get()))

    tk.Button(right_panel, text="저장", command=save_edited_event).grid(row=6, column=1, pady=10, sticky="n")

    # 취소 버튼
    tk.Button(right_panel, text="취소", command=lambda: display_view_event(str(cal.selection_get()))).grid(row=7, column=1, pady=5, sticky="n")


def display_add_event():
    clear_right_panel()

    # 제목 입력
    tk.Label(right_panel, text="제목 :", font=("Pretendard", 12)).grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")
    entry_event = tk.Entry(right_panel, width=40)
    entry_event.grid(row=0, column=1, padx=10, pady=(20, 5))

    # 위치 입력
    tk.Label(right_panel, text="위치 :", font=("Pretendard", 12)).grid(row=1, column=0, padx=10, pady=(20, 5), sticky="w")
    entry_location = tk.Entry(right_panel, width=40)
    entry_location.grid(row=1, column=1, padx=10, pady=(20, 5))

    # 저장 버튼
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

        if selected_date not in events:
            events[selected_date] = []
        events[selected_date].append({"이름": event_name, "위치": location})
        weather_label.config(text=f"{selected_date} 일정이 추가되었습니다.")
        clear_right_panel()

    tk.Button(right_panel, text="저장", command=save_event).grid(row=2, column=0, columnspan=2, pady=20)


def display_view_event(date):
    clear_right_panel()

    # 날짜 레이블
    date_label = tk.Label(right_panel, text=f"{date}", font=("Pretendard", 14))
    date_label.place(relx=0.5, rely=0.1, anchor="center")  # 중앙 상단에 날짜 배치

    if date in events:
        x_position = 50  # 첫 번째 박스의 x 값
        y_position = 100  # 첫 번째 박스의 y 값
        for event_info in events[date]:
            create_event_box(event_info, x=x_position, y=y_position)
            y_position += 100  # y 값을 증가하여 아래로 쌓기
    else:
        # 일정 없음 레이블
        no_event_label = tk.Label(right_panel, text="등록된 일정이 없습니다.", font=("Pretendard", 12))
        no_event_label.place(relx=0.5, rely=0.3, anchor="center")


def on_date_select(event):
    selected_date = str(cal.selection_get())

    # 선택된 날짜가 없을 경우 기본 메시지로 설정
    if not selected_date:
        weather_label.config(text="날짜를 선택해주세요.")
        return

    # 날짜 선택 시 초기화
    weather_label.config(text="")
    weather_icon_label.config(image="")
    recommendation_label.config(text="")

    # 선택된 날짜의 이벤트 표시
    display_view_event(selected_date)


def clear_right_panel():
    for widget in right_panel.winfo_children():
        if widget != weather_label_frame and widget != recommendation_label:
            widget.destroy()

    weather_label_frame.pack(expand=True)
    weather_label.pack()
    weather_icon_label.pack()
    recommendation_label.pack()


root = tk.Tk()
root.title("날씨 캘린더")
center_window(root, 1100, 600)

# Grid 레이아웃
root.rowconfigure(0, weight=1)  # 창 높이는 균등하게 분배
root.columnconfigure(0, weight=1)  # 왼쪽 패널
root.columnconfigure(1, weight=1)  # 오른쪽 패널

# Left Panel
left_panel = tk.Frame(root, background="lightblue", relief="solid", bd=1, width=550, height=600)
left_panel.grid(row=0, column=0, sticky="nsew")
left_panel.grid_propagate(False)  # 크기 고정
left_panel.pack_propagate(False)

cal = Calendar(left_panel,
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
               todayforeground='black')
cal.pack(expand=True, fill="both", padx=10, pady=10)

add_event_button = tk.Button(left_panel, text="일정 추가", command=display_add_event, anchor="center")
add_event_button.pack(pady=10)

# Right Panel
right_panel = tk.Frame(root, relief="solid", bd=1, width=550, height=600)
right_panel.grid(row=0, column=1, sticky="nsew")
right_panel.grid_propagate(False)  # 크기 고정
right_panel.pack_propagate(False)

# Weather Label Frame
weather_label_frame = tk.Frame(right_panel, relief="solid")
weather_label_frame.pack(fill="x", pady=10)

weather_label = tk.Label(weather_label_frame, text="날짜를 선택해주세요.", font=("Pretendard", 14))
weather_label.pack()

weather_icon_label = tk.Label(weather_label_frame)
weather_icon_label.pack()

# 추천 문구
recommendation_label = tk.Label(right_panel, text="", font=("Pretendard", 12), wraplength=400, justify="center")
recommendation_label.place(relx=0.5, rely=0.1, anchor="center")

# 날짜 선택 이벤트 바인딩
cal.bind("<<CalendarSelected>>", on_date_select)

root.mainloop()