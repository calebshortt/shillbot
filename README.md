# ShillBot

A Python-3 platform for identifying shills, trolls, or any other group of Reddit users based on their group's post history.

# Usage

To get ShillBot up and running, do the following:

    $ git clone https://github.com/calebshortt/shillbot.git
    $ cd ShillBot
    $ pip install -r requirements.txt
    $ mkdir resources
    $ cd resources
    $ touch shill_file.txt not_shill.txt

    Note: Sadly, you will have to populate the shill_file.txt and not_shill.txt files. These files will train the algorithm. Each line in the file should be a link to a reddit user. Example: https://www.reddit.com/user/<username>

    $ cd ..
    $ python start_mothership.py &
    $ python start_basic_worker <A username to check>


### Further Notes:

ShillBot is designed as a distributed system. As such, it has a main server (mothership) and the workers (clients) run their tasks and send their results to the mother ship. The mothership runs the analysis and maintains the model for the algorithm. In the provided instruction, the mothership is running in the background while the user is calling the start_basic_worker.py script.








