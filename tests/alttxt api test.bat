@echo off

cd ../data

rem // Verify error messages for all missing parameters - these should result in 400s
rem // Missing data file
curl -X POST -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Missing verbosity
curl -X POST -F "data=@movie_data_card_sort.json" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Missing level
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=high" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Missing explain
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=high" -F "level=2" "http://localhost:8000/api/alttxt/"
echo(
rem // Bad data file
curl -X POST -F "data=@../README.md" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Bad verbosity param
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=hello" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Bad level param
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=high" -F "level=hello" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Bad explain param
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=high" -F "level=2" -F "explain=hello" "http://localhost:8000/api/alttxt/"
echo(
rem // Aggregated file
curl -X POST -F "data=@agg_test.json" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Bad aggregateBy value
curl -X POST -F "data=@bad_agg_test.json" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // Bad value in json file
curl -X POST -F "data=@bad.json" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(

echo "=========================================="

rem // Tests for all valid combinations of parameters
rem // Low verbosity L1, explain simple, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=low" -F "level=1" -F "explain=simple" -F "title=A test plot" "http://localhost:8000/api/alttxt/"
echo(
rem // Low verbosity L1, explain full, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=low" -F "level=1" -F "explain=full" -F "title=Una visualizacion de probar" "http://localhost:8000/api/alttxt/"
echo(
rem // Medium verbosity L1, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=medium" -F "level=1" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // High verbosity L1, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=high" -F "level=1" -F "title=Who even reads titles anyway" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, low verbosity, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=low" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, medium verbosity, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=medium" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, high verbosity, card sort
curl -X POST -F "data=@movie_data_card_sort.json" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, low verbosity, dev sort
curl -X POST -F "data=@movie_data_dev_sort.json" -F "verbosity=low" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, medium verbosity, dev sort
curl -X POST -F "data=@movie_data_dev_sort.json" -F "verbosity=medium" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, high verbosity, dev sort
curl -X POST -F "data=@movie_data_dev_sort.json" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, low verbosity, degree sort
curl -X POST -F "data=@movie_data_degree_sort.json" -F "verbosity=low" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, medium verbosity, degree sort
curl -X POST -F "data=@movie_data_degree_sort.json" -F "verbosity=medium" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
echo(
rem // L2, high verbosity, degree sort
curl -X POST -F "data=@movie_data_degree_sort.json" -F "verbosity=high" -F "level=2" -F "explain=none" "http://localhost:8000/api/alttxt/"
pause