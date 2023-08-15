@echo off

cd ../

rem // Low verbosity L1, explain simple, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 1 --verbosity low --explain-upset simple --title "A test plot"
rem // Low verbosity L1, explain full, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 1 --verbosity low --explain-upset full --title "Una visualizacion de probar"

rem // Medium verbsity L1, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 1 --verbosity medium
rem // High verbosity L1, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 1 --verbosity high --title "Who even reads titles anyway"

rem // L2, low verbosity, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 2 --verbosity low
rem // L2, medium verbosity, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 2 --verbosity medium
rem // L2, high verbosity, card sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_card_sort.json" --level 2 --verbosity high
rem // L2, low verbosity, dev sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_dev_sort.json" --level 2 --verbosity low
rem // L2, medium verbosity, dev sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_dev_sort.json" --level 2 --verbosity medium
rem // L2, high verbosity, dev sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_dev_sort.json" --level 2 --verbosity high
rem // L2, low verbosity, degree sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_degree_sort.json" --level 2 --verbosity low
rem // L2, medium verbosity, degree sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_degree_sort.json" --level 2 --verbosity medium
rem // L2, high verbosity, degree sort
"venv\Scripts\python.exe" "src\alttxt" --data "data\movie_data_degree_sort.json" --level 2 --verbosity high
pause