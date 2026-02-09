/**
 * 價格圖表組件 - 顯示金銀價格趨勢
 */
import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

const PriceChart = ({ historicalData }) => {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        if (!chartRef.current) return;

        // 初始化圖表
        if (!chartInstance.current) {
            chartInstance.current = echarts.init(chartRef.current);
        }

        // 配置圖表
        const option = {
            title: {
                text: '金銀價格趨勢圖（TWD/錢）',
                left: 'center',
                textStyle: {
                    fontSize: 20,
                    fontWeight: 'bold',
                },
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                },
            },
            legend: {
                data: ['金價', '銀價'],
                top: 40,
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true,
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: historicalData?.timestamps?.map(ts => {
                    const date = new Date(ts);
                    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
                }) || [],
                axisLabel: {
                    rotate: 45,
                },
            },
            yAxis: [
                {
                    type: 'value',
                    name: '金價 (TWD)',
                    position: 'left',
                    axisLabel: {
                        formatter: '{value}',
                    },
                },
                {
                    type: 'value',
                    name: '銀價 (TWD)',
                    position: 'right',
                    axisLabel: {
                        formatter: '{value}',
                    },
                },
            ],
            series: [
                {
                    name: '金價',
                    type: 'line',
                    smooth: true,
                    data: historicalData?.gold_prices || [],
                    itemStyle: {
                        color: '#FFD700',
                    },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(255, 215, 0, 0.5)' },
                            { offset: 1, color: 'rgba(255, 215, 0, 0.1)' },
                        ]),
                    },
                    yAxisIndex: 0,
                },
                {
                    name: '銀價',
                    type: 'line',
                    smooth: true,
                    data: historicalData?.silver_prices || [],
                    itemStyle: {
                        color: '#C0C0C0',
                    },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(192, 192, 192, 0.5)' },
                            { offset: 1, color: 'rgba(192, 192, 192, 0.1)' },
                        ]),
                    },
                    yAxisIndex: 1,
                },
            ],
        };

        chartInstance.current.setOption(option);

        // 響應式調整
        const handleResize = () => {
            chartInstance.current?.resize();
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [historicalData]);

    return (
        <div
            ref={chartRef}
            style={{
                width: '100%',
                height: '500px',
                backgroundColor: '#fff',
                borderRadius: '8px',
                padding: '20px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            }}
        />
    );
};

export default PriceChart;
