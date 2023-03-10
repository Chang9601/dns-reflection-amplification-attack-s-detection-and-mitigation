# DNS 증폭 공격 탐지와 완화

## 소개
* DNS 증폭 공격 탐지와 완화를 구현한다.

## 목적
* DDoS 공격 중 하나인 DNS 증폭 공격의 원리를 이해한다.
* DNS 증폭 공격을 탐지하고 완화하는 기술을 배우고 구현한다.
* SDN의 Flow Rule을 이해하고 적용한다.

## 조건

### 탐지
* 모니터에 도착하는 패킷을 확인해서 DNS 요청 패킷인지 아니면 DNS 응답 패킷인지 확인한다.
  * DNS 요청 패킷일 경우, DNS 식별 번호를 원본 IP 주소에 매핑한다.
  * DNS 응답 패킷일 경우, 동일한 DNS 식별 번호가 존재하는지 확인한다.
    * 만약 동일한 식별 번호가 존재하지 않을 경우 대상 IP 주소를 기준으로 일치하지 않는 응답의 개수를 증가시킨다.
	* 만약 이 개수가 50을 넘어가는 호스트가 존재할 경우, 완화가 시작되어야 한다. 

### 완화
* 공격을 받는 호스트를 탐지하고 난 후, 그 호스트로 전달되는 모든 DNS 응답을 떨어뜨리는데 모니터가 파악한 정당한 DNS 응답은 제외한다. (즉, DNS 요청 패킷이 존재)
  * 피해 호스트에 대한 일치하지 않는 응답의 개수가 50을 스위치 s1에 흐름 규칙을 설치해서 패킷을 떨어뜨린다.
  * 정당한 응답을 허용하기 위해서 호스트로부터 새로운 DNS 쿼리를 보면 흐름 규칙을 설치하고 DNS 리졸버로부터 상응하는 응답을 보면 흐름 규칙을 삭제한다.

## 기능
* DNS 증폭 공격을 탐지하고 완화

## 제작 기간
* 2023.01.02 - 2023.01.09

## 출처
* Purdue University (CS 422: Computer Networks)
* 직접 작성한 코드: py-src 디렉토리의 소스 파일 (start_dns_monitor.py의 TODO)