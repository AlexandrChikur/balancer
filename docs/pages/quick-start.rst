============
Quick start
============

For run the balancer you should have a Python 3.10 and higher on your machine and that's enough ... or not ?

Is the best way to run balancer is to use a `Poetry <https://python-poetry.org/>`_ (here it's v1.2.2)
But for quick set up and run the balancer you can use requirements.txt file


* `Installation`_
* `Configuration`_
* `Simple start`_
* `Start with the Poetry`_



-------------
Installation
-------------

On Linux
========
Change directory to the folder where the balancer will be.

And then use :code:`wget` utility to download:

..  code-block:: bash

    sudo wget https://github.com/AlexandrChikur/balancer/archive/refs/tags/v.1.0.0.tar.gz


Then unarchive it with:

..  code-block:: bash

    sudo tar -xvf balancer-v.1.0.0.tar.gz


On Windows
===========
Simple way is to download source code from `releases page <https://github.com/AlexandrChikur/balancer/releases>`_

Unarchive it more comfortable way for you.

-------------
Configuration
-------------
Config structure looks pretty simple:

..  code-block:: yaml

    # Config values related to balancer
    balancer:
      targets: # List of targets between those load will be distributed.
        target_1: # Target name. Doesn't really matter. It can be used for debugging convenience, for example
          host: localhost # Target host
          port: 4001      # Target host
    #    target_2:
    #      host: target_2
    #      port: 4002
    #  ...
    #  and go on
      balance_algorithm: 'round-robin' # Algorithm that balancer should to use. Able to: 'random', 'round-robin'

Create :code:`.yaml` settings file following structure above whatever you want
(you will able to provide absolute path to it, or leave it in balancer folder
if you dont want to use it as option when run balancer)

-------------
Simple start
-------------
Move to balancer folder and ...

First, create virtual environment and install dependencies:

..  code-block:: bash

    python -m venv .venv
    python -m pip install -r requirements.txt


Activate venv using:

..  code-block:: bash
    :caption: Linux

    source .venv/bin/activate

..  code-block:: bash
    :caption: Windows PowerShell

    .venv\Scripts\activate.ps1

..  code-block:: bash
    :caption: Windows CMD

    .venv\Scripts\activate.bat

About active virtual environment will indicate it's name on each line of your CLI.


So, here you ready to start the balancer:

You can use :code:`python .\balancer.py --help` to see more information about options.

You will see:

..  code-block:: bash

    Usage: balancer.py [OPTIONS]

    Options:
      --config TEXT              [required]
      --logs TEXT                Path to directory where logs will be stored
                                 [default: \var\log\load_balancer]
      --port INTEGER             [default: 3333]
      --max-connections INTEGER  [default: 21]
      --help                     Show this message and exit.


..  code-block:: bash
    :caption: Run balancer

    python balancer.py --port 3333 --config path/to/settings.yaml --logs /path/to/logs/

Congratulations! It works!

..  code-block:: bash
    :caption: Run balancer

    [INFO][MainThread][MainProcess] 2022-11-08 08:44:28,620 | Start BALANCER v.1.0.0
      _______   ________   __       ________   ___   __    ______   ______   ______
    /_______/\ /_______/\ /_/\     /_______/\ /__/\ /__/\ /_____/\ /_____/\ /_____/\
    \::: _  \ \\::: _  \ \\:\ \    \::: _  \ \\::\_\\  \ \\:::__\/ \::::_\/_\:::_ \ \
     \::(_)  \/_\::(_)  \ \\:\ \    \::(_)  \ \\:. `-\  \ \\:\ \  __\:\/___/\\:(_) ) )_
      \::  _  \ \\:: __  \ \\:\ \____\:: __  \ \\:. _    \ \\:\ \/_/\\::___\/_\: __ `\ \
       \::(_)  \ \\:.\ \  \ \\:\/___/\\:.\ \  \ \\. \`-\  \ \\:\_\ \ \\:\____/\\ \ `\ \ \
        \_______\/ \__\/\__\/ \_____\/ \__\/\__\/ \__\/ \__\/ \_____\/ \_____\/ \_\/ \_\/


    [INFO][MainThread][MainProcess] 2022-11-08 08:44:28,621 | With using configuration:
            targets:
                    target_1:
                            host = localhost
                            port = 4001
            balance_algorithm = round-robin
    [INFO][MainThread][MainProcess] 2022-11-08 08:44:28,622 | Add target: <Target name=target_1 host=localhost port=4001)> for load distribution
    [INFO][MainThread][MainProcess] 2022-11-08 08:44:28,622 | Balancer initialization: <Balancer host=0.0.0.0 port=3333 algorithm=ROUND_ROBIN targets_amount=1> completed successfully

----------------------
Start with the Poetry
----------------------

Will be soon ...
