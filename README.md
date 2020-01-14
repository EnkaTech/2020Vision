# 2020 Vision
Vision code for the 2020 FRC season

  - **main_server.py:** Main program for testing in a network without a RoboRIO.
  - **main_client.py:** Same as main_server.py, but connects to an existing NetworkTables instance in the network.
  - **proc_helper.py:** Vision algorithms used in the main program.
  - **install.sh:** Bash script for moving the .py and .service files in intended locations. This is required for automatically starting the progaram upon the boot process. Must be run as root and from this directory.
  - **2020vision.service: SystemD unit file for automatically running the program upon boot.

## Configuring SystemD for autorun

After running install.sh, tell SystemD to check for new unit files:

```bash
sudo systemctl daemon-reload
```

Now you can autorun the program by simply typing:

```bash
sudo systemctl enable 2020vision.service
```

The program will run in the background starting with the next boot.
You can disable the service to stop running the program every boot sequence.

```bash
sudo systemctl disable 2020vision.service
```