#!/bin/bash

x=1
while [ $x -le 5 ]
do
	cat vf_test_camera/tests/camera/rcv_cam_on.log | awk '{print $1" "$2"#"$4$5$6$7$8$9$10$11}'|
#	cat /home/dhorovyi/PycharmProjects/camera/vf_test_camera/tests/camera/rcv_cam_on.log | awk '{print $1" "$2"#"$4$5$6$7$8$9$10$11}'|
	while read msg;
	do cansend $msg;
	done
	x=$(( $x + 1 ))
	sleep 3
done
