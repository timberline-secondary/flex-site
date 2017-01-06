if [ "$1" = "runserver" ]; then
	if [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
		#Windows NT platform
		echo "Operating System: Windows"
		source Scripts/activate
		winpty python ./src/manage.py runserver

	elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
		#Linux platform
		echo "Operating System: Linux"
		source bin/activate
		python ./src/manage.py runserver
	fi

elif [ "$1" = "setup" ]; then
	if [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
		#Windows NT platform
		echo "Operating System: Windows"
		source Scripts/activate
		winpty python ./src/manage.py makemigrations events
		winpty python ./src/manage.py migrate
		winpty python ./src/manage.py loaddata src/events/fixtures/initdata.json
		winpty python ./src/manage.py createcachetable
		winpty python ./src/manage.py makemigrations
		winpty python ./src/manage.py migrate
		winpty python ./src/manage.py createsuperuser

	elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
		#Linux platform
		echo "Operating System: Linux"
		source bin/activate
		python ./src/manage.py makemigrations events
		python ./src/manage.py migrate
		python ./src/manage.py loaddata src/events/fixtures/initdata.json
		python ./src/manage.py createcachetable
	  	python ./src/manage.py makemigrations
		python ./src/manage.py migrate
		python ./src/manage.py createsuperuser
	fi

elif [ "$1" = "help" ]; then
	echo "usage: ./setup.sh [parameter]"
	echo " "
	echo "  [available parameters]"
	echo "  setup - prepares the django project"
	echo "  runserver - runs the server"
else
	echo "Type --help for a list of commands"
fi
