@echo off

REM Check if arguments are provided
IF "%1"=="skip" (
    echo Skipping data python scrips
) ELSE (
    python data_formatter.py
    python data_summer.py
    python data_averager.py
)

python stacked_bar_graph.py
python stacked_bar_graph.py all
python stacked_line_graph.py
python stacked_line_graph.py all
python fps_scatter.py
