jtime
=====
[![Build Status](https://travis-ci.org/mapmyfitness/jtime.png?branch=master)](https://travis-ci.org/mapmyfitness/jtime)
[![Coverage Status](https://coveralls.io/repos/mapmyfitness/jtime/badge.png)](https://coveralls.io/r/mapmyfitness/jtime)
[![PyPi version](https://pypip.in/v/jtime/badge.png)](https://crate.io/packages/jtime/)
[![PyPi downloads](https://pypip.in/d/jtime/badge.png)](https://crate.io/packages/jtime/)

jtime - A simple tool that provides git-aware time-tracking against JIRA issues without having to leave the command-line.


## Basic Workflow
```
$ git checkout -b SOC-2355
$ jtime mark
Set mark at 4:50 PM on SOC-2355 by changing status to "In Progress"
 
# Work for 5 minutes
 
$ jtime status
(SOC-2355) Backend: Implement notification message types
  Status: In Progress as of Mon 02/24/14 04:50 PM
  Assignee: allan.glen
Time logged (0m):
  No worklogs
5m elapsed (use "jtime log ." to log elapsed time or "jtime log <duration> (ex. 30m, 1h etc.)" to log a specific amount of time)
 
# Log 5 minutes of time (or just use 'jtime log .' to log all elapsed time)
$ jtime log 5m
Logged 5m against issue SOC-2355
 
# Do some more work (22 minutes) but get asked to look at another branch.  Log time on the current branch before switching.
 
$ jtime log .
Logged 22m against issue SOC-2355
 
# Checkout the other branch and log some time (but don't mark the ticket since it isn't mine)
 
$ git checkout API-1234
$ jtime log 30m
Logged 30m against issue API-1234
 
# Back to work on SOC-2355..  mark it after checkout to start counting from now
$ git checkout SOC-2355
$ jtime mark
Set mark at 18:14:23 on SOC-2355 by touching last work log
 
# 68 minutes pass..
 
$ jtime status
(SOC-2355) Backend: Implement notification message types
  Status: In Progress as of Mon 02/24/14 04:50 PM
  Assignee: allan.glen
Time logged (36m):
  Mon 02/24/14 03:52 PM - allan.glen (5m): Working on issue SOC-2355
  Mon 02/24/14 04:44 PM - allan.glen (22m): Working on issue SOC-2355
68m elapsed (use "jtime log ." to log elapsed time or "jtime log <duration> (ex. 30m, 1h etc.)" to log a specific amount of time)
 
$ jtime log . -m "Done for the day.."
Logged 68m against issue SOC-2355 (Done for the day..)
 
$ jtime status
(SOC-2355) Backend: Implement notification message types
  Status: In Progress as of Mon 02/24/14 04:50 PM
  Assignee: allan.glen
Time logged (36m):
  Mon 02/24/14 03:52 PM - allan.glen (5m): Working on issue SOC-2355
  Mon 02/24/14 04:44 PM - allan.glen (22m): Working on issue SOC-2355
  Mon 02/24/14 05:14 PM - allan.glen (68m): Done for the day..
0m elapsed
 
# Go home for the day.  Mark the ticket the next morning and keep rolling..
$ jtime mark
Set mark at 08:35 AM on SOC-2355 by touching last work log
```

## Installation
```
pip install jtime
jtime config
```
