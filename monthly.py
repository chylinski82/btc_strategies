import argparse
from datetime import datetime
import re
from collections import defaultdict

def parse_trades(trade_file):
    trades = []
    with open(trade_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            try:
                _, rest = line.strip().split(": ", 1)
                date_action, size, cash = rest.split(", ", 2)
                date_str, action = date_action.split(" ", 1)
                date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                cash_value = float(cash.split('=')[1])
                trades.append((date, action.strip(), cash_value))
            except Exception as e:
                print(f"Error parsing line: {line}. Error: {str(e)}")
    return trades

def summarize_trades(trades):
    summary = defaultdict(list)
    for trade in trades:
        date, action, cash = trade
        month_year = date.strftime("%b-%Y")
        summary[month_year].append(cash)
    return summary

def write_summary(summary, output_file):
    with open(output_file, 'w') as file:
        file.write("Month-Year, Profit, Cash up to date\n")
        for month_year, cash_values in summary.items():
            start_cash = cash_values[0]
            end_cash = cash_values[-1]
            profit = end_cash - start_cash
            file.write(f"{month_year}, {profit:.2f}, {end_cash:.2f}\n")

def main():
    parser = argparse.ArgumentParser(description='Parse and summarize trading data.')
    parser.add_argument('input_file', type=str, help='Input file containing trading data.')
    parser.add_argument('output_file', type=str, help='Output file to write summary.')
    args = parser.parse_args()

    trades = parse_trades(args.input_file)
    summary = summarize_trades(trades)
    write_summary(summary, args.output_file)

if __name__ == "__main__":
    main()
