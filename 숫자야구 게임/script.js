// ===== 전역 변수 및 요소 선언 =====
let attempts = 9; // 남은 시도 횟수
let answer = []; // 정답 숫자 3개 배열

const number1 = document.getElementById('number1');
const number2 = document.getElementById('number2');
const number3 = document.getElementById('number3');

// ===== 게임 초기화 =====
function initGame(){
    // 시도 횟수 초기화
    attempts = 9;
    answer = [];

    // 중복되지 않는 랜덤 숫자 3개 push
    while (answer.length < 3){
        let num = Math.floor(Math.random()*10);
        if(!answer.includes(num))
            answer.push(num);
    }

    // input 초기화
    number1.value = '';
    number2.value = '';
    number3.value = '';

    // 남은 횟수 표시 및 결과창 초기화
    document.getElementById('attempts').textContent = attempts;
    document.getElementById('results').innerHTML = '';

}

initGame();

// ===== 숫자 확인  =====
function check_numbers(){
    let a = number1.value;
    let b = number2.value;
    let c = number3.value;
    
    // 입력 유효성 검사
    // 빈 칸이 있으면 input 비우고 종료
    if (a === '' || b === '' || c === ''){
        number1.value = '';
        number2.value = '';
        number3.value = '';
        return;
    }

    let strike = 0;
    let ball = 0;

    let input = [a, b, c];

    // 숫자 비교
    // 자리 + 값이 맞으면 strike, 값만 맞으면 ball
    for(let i = 0; i < 3; i++){
        if(Number(input[i]) === answer[i]){
            strike++;
        }
        else if(answer.includes(Number(input[i]))){
            ball++;
        }
    }

    // 결과 생성
    let result;

    // 아웃이면 "O", 아니면 nS nB 출력
    if (strike === 0 && ball === 0){
        result = '<span class="num-result out">O</span>';
    }
    else{
        result = strike + '<span class="num-result strike">S</span>' + ball + '<span class="num-result ball">B</span>';
    }

    // 결과 화면에 누적 출력
    let row = '<div class="check-result"><span class="left">'+ a + ' ' + b + ' ' + c + '</span><span>:</span><span class="right">' + result + '</span></div>';
    document.getElementById('results').innerHTML += row;
    
    // 남은 횟수 감소 및 갱신
    attempts--;
    document.getElementById('attempts').textContent = attempts;

    // input 비우기
    number1.value = '';
    number2.value = '';
    number3.value = '';

    // 게임 종료 조건 처리
    // 3스트라이크면 승리, 횟수 소진시 패배
    if (strike === 3){
        document.getElementById('game-result-img').src = 'success.png'; // 성공시 이미지 출력
        document.querySelector('.submit-button').disabled = true; // 버튼 비활성화
    }

    else if (attempts === 0){
        document.getElementById('game-result-img').src = 'fail.png'; // 실패시 이미지 출력
        document.querySelector('.submit-button').disabled = true; // 버튼 비활성화
    }
}