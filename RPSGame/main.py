import cv2 as cv
import mediapipe as mp
import math, time
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions
from visualization import draw_manual, print_RSP_result

# --- MediaPipe 손 인식기 설정 ---
model_path = "hand_landmarker.task"

options = vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=vision.RunningMode.VIDEO,  # 실시간 영상용
    num_hands=1,                            # 손 1개만 인식
)

detector = vision.HandLandmarker.create_from_options(options)


# --- 가위바위보 판별 함수 ---
def get_rps(detection_result):
    # 손 인식 안 되면 None
    if detection_result is None or not detection_result.hand_landmarks:
        return None

    landmarks = detection_result.hand_landmarks[0]
    wrist = landmarks[0]  # 손목

    # 손목~특정 점 거리 계산 함수
    def dist(p):
        return math.sqrt((p.x - wrist.x)**2 + (p.y - wrist.y)**2)

    # 검지, 중지, 약지, 소지의 (TIP, PIP) 번호
    fingers = [(8, 6), (12, 10), (16, 14), (20, 18)]

    open_count = 0
    for tip, pip in fingers:
        if dist(landmarks[tip]) > dist(landmarks[pip]):  # TIP이 더 멀면 펴짐
            open_count += 1

    # 펴진 손가락 수로 판정 (0=Rock, 1=Paper, 2=Scissors)
    if open_count == 0:
        return 0  # 바위
    elif open_count == 2:
        return 2  # 가위
    elif open_count == 4:
        return 1  # 보
    else:
        return None  # 애매하면 판정 안 함


# --- 메인 실행 루프 ---
if __name__ == "__main__":
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting ...")
            break

        # 좌우 반전 (거울처럼 보이게)
        frame = cv.flip(frame, 1)

        # OpenCV(BGR) → MediaPipe(RGB) 변환
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # 타임스탬프 (VIDEO 모드는 필수)
        timestamp = int(time.time() * 1000)

        # 손 인식 실행
        detection_result = detector.detect_for_video(mp_image, timestamp)

        # 가위바위보 판별
        rps_result = get_rps(detection_result)

        # 화면에 랜드마크 + 결과 그리기
        frame = draw_manual(frame, detection_result)
        frame = print_RSP_result(frame, rps_result)

        cv.imshow('RPS Game', frame)
        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()