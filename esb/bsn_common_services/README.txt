This is the location of the the BSN common services which are deployed
in production.

Deployment Server: qa-esb-services1
BigRobot Path:     /home/bsn/workspace/bigrobot
Log path:          /home/bsn/bigrobot_esb_log


ESB service startup instruction:
- Log into deployment server
- Start a 'screen' session
- cd /home/bsn/workspace/bigrobot/esb/bsn_common_services
- Start the service daemon:
    $ ./start_services.sh | tee -a /home/bsn/bigrobot_esb_log/start_services-bsn_common_services.log
- Leave the session running inside 'screen'. You can close the terminal window.

- To connect to a running 'screen' session, log into qa-esb-services1 and type
  'screen -r'. Copy the screen ID and then run 'screen -rD <screen_id>' to
  connect to it.


Service implementation details:
- The file tasks.py contains the task implementations. We can define multiple
  classes as a way to group together similar actions (e.g., UpgradeCommands
  class).
- To use these tasks, do the following in your keyword file:

        from bsn_common_services import tasks as tasks
        t = test.Test()
        task = tasks.UpgradeCommands()

        res1 = task.cli_copy_upgrade_pkg.delay(t.params(), src=image, node=node)
        res2 = task.cli_stage_upgrade_pkg.delay(t.params(), node=node)
        ...

Updating services:
- Whenever changes are made to the services (bigrobot/esb/bsn_common_services),
  you need to redeploy the service.
- Log into the deployment server (as described in the section above) and kill
  the service daemon - press Control-C.
- Update the branch using 'git pull'
    $ git pull
- Restart the service daemon:
    $ ./start_services.sh
