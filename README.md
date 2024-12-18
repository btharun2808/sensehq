# sensehq
Assignment

OS Used: CentOS Linux release 7.6.1810 (Core)
Python Version: 3.7

Arguments:
--interval: default value-5
--format: default value - text
--output: optional argument which saves the output in the given name.

Commands:

python monitor_system.py 
python monitor_system.py --interval 10
python monitor_system.py --interval 10 --format json

Instructions:
python3 -m venv monitoring_scripts
source monitoring_scripts/bin/activate
cp monitor_system.py monitoring_scripts/
pip install psutil
Run the above commands.
