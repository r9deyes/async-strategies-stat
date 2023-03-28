export RANDOM_SEED=1234;
python3.10 ./random_/build_csv.py gather --coroutines-count 20:50 --coroutines-limit 20:50 --await-count 10:50:5 | tee rand-gather.csv;
python3.10 ./random_/build_csv.py sem_gather --coroutines-count 20:50 --coroutines-limit 20:50 --await-count 10:50:5 | tee rand-sem-gather.csv;
python3.10 ./random_/build_csv.py chunked_gather --coroutines-count 20:50 --coroutines-limit 20:50 --await-count 10:50:5 | tee rand-chunked-gather.csv;
python3.10 ./random_/build_csv.py queue --coroutines-count 20:50 --coroutines-limit 20:50 --await-count 10:50:5 | tee rand-queue.csv;
git add .;
git commit -a -m 'added results';
git push origin results;
