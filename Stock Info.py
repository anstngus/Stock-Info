#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 3 16:56:51 2024

@author: moonsoohyun
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup

usd_to_krw = 0
krw_to_usd = 0
usd_to_krw_change = 0

def main():
    tickers = input("주식 티커를 입력하세요. (여러개인 경우 쉼표로 구분합니다.): ").split(",")  #주식 데이터를 입력하고, 쉼표로 구분된 것을 하나의 객체로 나눔(split)

    global usd_to_krw, krw_to_usd, usd_to_krw_change #전역 변수 설정
    
    usd_to_krw, usd_to_krw_change = exchange_rate() #두 값을 받아옴

    for ticker in tickers:
        ticker = ticker.strip().upper() #공백을 삭제하고, 입력값을 대문자로 변환하여 일관성을 유지

        if ticker == "USD-KRW":
            print(f"현재 환율은 {usd_to_krw}원 이며, 등락률은 {usd_to_krw_change}% 입니다.")
            quit()
        
        elif ticker.isdigit():
            deserv_naver_finance(ticker)
        else:
            deserv_yahoo_finance(ticker)

    print(f"현재 환율은 {usd_to_krw}원 이며, 등락률은 {usd_to_krw_change}% 입니다.")
            

def exchange_rate():    #환율 데이터 가져오기
    try:
        url = "https://finance.naver.com/marketindex/"
        response = requests.get(url)
        response.raise_for_status() #요청에 실패하면 예외 상황 발생

        soup = BeautifulSoup(response.text, 'html.parser')

        #print(soup.prettify())

        usd_to_krw_element = soup.select_one('div.market1 span.value')
        if usd_to_krw_element: #값이 존재하는지 확인
            usd_to_krw = float(usd_to_krw_element.get_text().replace(",", ""))
        else:
            print("환율 데이터를 불러오는 중 실패하였습니다.")
            return None, None
        
        usd_to_krw_change_element = soup.select_one('div.market1 span.change')
        usd_to_krw_change = float(usd_to_krw_change_element.get_text().replace(",", ""))
        return usd_to_krw, usd_to_krw_change
                        
    except Exception as excp:
        print(f"오류 발생: {excp}")
        return None


def deserv_yahoo_finance(ticker): #yahoo finance에서 데이터 가져오기
    global usd_to_krw
    if usd_to_krw == 0:
        usd_to_krw == get_exchange_rate()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice')
        yesterday_close_price = info.get('regularMarketPreviousClose')
        change_percent = ((current_price - yesterday_close_price) / yesterday_close_price) * 100

        print("\n=====해외 주식(Yahoo Finance 제공)=====\n")
        print(
            f"주식명: {info.get('longName') or info.get('shortName')}\n"
            f"거래소: {info.get('exchange')}\n"
            f"국가: {info.get('country')}\n"
            f"분야: {info.get('sector')}\n"
            f"현재 주가는 {info.get('currentPrice')} {info.get('currency')}, 약 {info.get('currentPrice')* usd_to_krw:.2f}원 입니다.\n"
            f"현재 거래량은 {info.get('volume')}주\n"
            f"현재 등락률은 {change_percent:.2f}%\n"
            f"52주 최고가는 {info.get('fiftyTwoWeekHigh')} {info.get('currency')}, 약 {info.get('currentPrice')* usd_to_krw:.2f}원 입니다.\n"
            f"52주 최저가는 {info.get('fiftyTwoWeekLow')} {info.get('currency')}, 약 {info.get('currentPrice')* usd_to_krw:.2f}원 입니다.\n"
            f"목표가는 {info.get('targetMeanPrice')} {info.get('currency')}, 약 {info.get('currentPrice')* usd_to_krw:.2f}원 입니다.\n"
            f"현재 전문가 추천 상태는 {info.get('recommendationKey')}, {info.get('recommendationMean')} 입니다\n"
            f"\n=====요청하신 모든 정보 불러오기를 성공했습니다.=====\n"
            )
                               
    except Exception as excp:
        print(f"{ticker}의 정보를 가져오는 중 오류가 발생했습니다. 오류 코드: {excp}\n")

def deserv_naver_finance(ticker): #네이버 금융에서 정보 가져오기
    try:
        url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        company_name_element = soup.select_one('div.wrap_company h2')
        company_name = company_name_element.get_text() if company_name_element else "정보 없음"

        price_element = soup.select_one('p.no_today .blind')
        price = price_element.get_text() if price_element else "정보 없음"

        """price_change_rate_element = soup.select_one('p.no_exday span')
        if len(price_change_rate_element) > 1:
            price_change_rate = price_change_element[1].get_text()
        else:
            price_change_rate = "정보 없음"
        """

        print("국내 주식(네이버 금융 제공)")
        print(f"{company_name}의 현재 주가는 {price}원입니다.")
        
    except Exception as excp:
        print(f"{ticker}의 정보를 가져오는 중 오류 발생: {excp}")

if __name__ == "__main__":
    main()
