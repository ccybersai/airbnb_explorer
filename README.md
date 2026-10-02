```bash
bash setup.sh
source venv/bin/activate

python main.py --help
python main.py --summary
python main.py --search neighborhood "khlong toei"
python main.py --search price 1000-2000
python main.py --aggregate neighborhood
python main.py --aggregate room_type
python main.py --plot price_dist
python main.py --plot neighborhood --format jpg
python main.py --export budget.csv --search price 500-1500 --columns id name neighborhood room_type price

python -m pytest -v
```