// 장현욱

import React from 'react';
import ReactApexChart from 'react-apexcharts';
import style from './Statistics.module.css'
import ApexCharts from 'apexcharts';


const Statistics: React.FC = () => {

    const series = [{
        name: "선호도 비율",
        data: [{
            x: '1',
            y: 400
        }, {
            x: '2',
            y: 430
        }, {
            x: '3',
            y: 448
        }, {
            x: '4',
            y: 170
        }, {
            x: '5',
            y: 540
        }, {
            x: '6',
            y: 580
        }, {
            x: '7',
            y: 690
        }, {
            x: '8',
            y: 990
        }, {
            x: '9',
            y: 690
        }, {
            x: '10',
            y: 690
        }]
    }];
    // 가장 낮은 값 찾기
    const minY = Math.min(...series[0].data.map(item => item.y));
    // 가장 높은 값 찾기
    const maxY = Math.max(...series[0].data.map(item => item.y));
    // 가장 높은 값을 가진 X
    const maxYPoint = series[0].data.reduce((max, p) => p.y > max.y ? p : max, series[0].data[0]);


    // 각 막대의 색상 결정
    const barColors = series[0].data.map(item => {
        if (item.y === maxY) return '#6366F1'; // Y가 가장 큰 값 색
        if (item.y === minY) return '#DC2626'; // Y가 가장 작은 값 색
        return '#6B7280'; // 나머지 값은 파란색
    });
    const options: ApexCharts.ApexOptions = {
        // 그래프 타입, 크기 지정
        chart: {
            type: 'bar',
            height: 380,
            toolbar: {
                show: false, // 차트의 도구 모음을 숨깁니다.
            },
        },

        // 그래프의 제목
        title: {
            text: '시간대별 만족도',
            style: {
                color: '#FFFFFF', // 제목 글자색을 하얀색으로 설정
            }
        },

        // 그래프의 부제목
        subtitle: {
            text: `(게임제목)은 ${maxYPoint.x}시간 이상의 플레이타임을 추천합니다.`, // 부제목에 추가 텍스트를 표시
            // align: 'center',
            style: {
                color: '#FFFFFF', // 부제목 글자색을 하얀색으로 설정
            }
        },

        // 그래프 아래(x좌표에) 나올 값
        xaxis: {
            type: 'category',
            labels: {
                formatter: function (val:string) {
                    return val + '시간';
                },
                style: {
                    colors: '#FFFFFF', // x축 레이블 글자 색을 하얀색으로 설정
                    fontSize: '12px', // 선택적: 글자 크기도 조정할 수 있습니다
                    // 추가적인 스타일 속성을 여기에 설정할 수 있습니다.
                }
            }
        },

        // 그래프 왼쪽(y좌표에) 나올 값
        yaxis: {
            labels: {
                style: {
                    colors: ['#FFFFFF'], // y축 레이블 글자 색을 하얀색으로 설정
                }
            }
        },

        // 각각의 막대에 색을 다르게 하기위한 함수
        plotOptions: {
            bar: {
                horizontal: false, // 가로 세로 바꾸는 함수
                distributed: true // 각 막대별로 다른 색상 적용
            }
        },
        colors: barColors, // 위의 barColors에 맞게 색상 입히기

        // 호버시 툴팁 옵션
        tooltip: {
            theme: 'dark', // 'dark' 테마는 배경을 어둡게 하지만, 여기서는 Gray로 커스텀 필요
            style: {
                // backgroundColor: 'gray', // 툴팁 배경색을 Gray로 설정
                // color: '#FFFFFF', // 툴팁 글자색 설정
                fontSize: '12px',
            },
            y: {
                formatter: function (val: number) { // 타입스크립트 정의
                    if (val === maxY) {
                        return `${val}% - 대유쾌마운틴`; // 가장 높은 값을 가진 데이터 포인트에 "Best" 추가
                    } else if (val === minY) {
                        return `${val}% - 노잼사 구간`; // 가장 높은 값을 가진 데이터 포인트에 "Best" 추가
                    }
                    return `${val}%`;
                }
            }
        },

        // 막대 자체의 속성
        dataLabels: {
            enabled: true,
            //   textAnchor: 'start', 텍스트 위치
            style: {
                colors: ['#FFF'],  // 그래프 안의 숫자 색
                fontSize: '12px'
            },
            formatter: function (val: number) { // 타입스크립트 형식 구성
                return `${val}%`
            },
            offsetX: 0, // 왼쪽 마진
            dropShadow: {
                enabled: false
            }
        },

        // 막대 그래프 테두리
        stroke: {
            width: 1,
            // colors: ['#ebfbff']
        },

        // 각 그래프에 대한 설명
        legend: {
            labels: {
                colors: '#FFFFFF', // This will set the legend labels to white
            },
        },

    };

    return (
        <div className="flex justify-center px-40"> {/* p-16을 p-60 또는 원하는 크기로 조정 */}
            <div className={` ${style.neonBorder} w-full max-w-screen-lg bg-gray-900 rounded-xl`}> {/* 네온 효과 스타일을 적용합니다 */}
                <ReactApexChart options={options} series={series} type="bar" height={380} />
            </div>
        </div>
    );
}

export default Statistics;