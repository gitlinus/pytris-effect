#!/usr/bin/env bash
current_dir=$(basename $PWD)
if [ $current_dir == "pytris-effect" ]
then
	if [ -d ".venv" ]
	then
		source .venv/bin/activate
		echo "Launching Pytris Effect"
		python3 __main__.py
		echo "Thanks for playing Pytris Effect"
		deactivate || conda deactivate || source deactivate
	else
		echo "Virtual Environment missing"
		if [ -f "setup.sh" ]
		then
			echo "Running setup..."
			source setup.sh
		else
			echo "Setup file missing"
			echo "Creating setup file..."
			touch setup.sh
			echo "#!/usr/bin/env bash" >> setup.sh
			echo "python3 -m venv .venv" >> setup.sh
			echo "source .venv/bin/activate" >> setup.sh
			echo "python3 -m pip install -r requirements.txt" >> setup.sh
			echo "deactivate || conda deactivate || source deactivate" >> setup.sh
			source setup.sh
		fi
		source run.sh
	fi
else
	cd "$(dirname "${BASH_SOURCE[0]}")"
	current_dir=$(basename $PWD)
	if [ $current_dir == "pytris-effect" ]
	then
		source run.sh
	else
		echo "pytris-effect repository missing"
	fi
fi
