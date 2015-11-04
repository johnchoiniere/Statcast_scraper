'''
Copyright (C) 2015
Author: John Choiniere

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import os
import sys
game_numbers =[
'413649',
'413650',
'413651',
'413652',
'413653',
'413654',
'413655',
'413656',
'413657',
'413658',
'413659',
'413660',
'413661',
'413662',
'413663',
'413664',
'413665',
'413666',
'413667',
'413668',
'413669',
'413670',
'413671',
'413672',
'413673',
'413674',
'413675',
'413676',
'413677',
'413678',
'413679',
'413680',
'413681',
'413682',
'413684',
'413685',
'413693'
]

g=0
urlbase = "http://gd2.mlb.com/components/game/play-builder/"

for game in game_numbers:
	cwd = os.getcwd()
	if sys.platform=='linux':
		if not os.path.isdir(cwd+"/"+str(game)):
			os.mkdir(cwd+"/"+str(game))
	elif sys.platform=='win64' or sys.platform=='win32':
		if not os.path.isdir(cwd+"\\"+str(game)):
			os.mkdir(cwd+"\\"+str(game))
	else:
		print("OS not recognized; check source code and modify as necessary for compatibility")
		quit()
	os.chdir(str(game))
	statsapi_url = "http://statsapi.mlb.com/api/v1/game/"+str(game)+"/feed/color"
	statsapi_data = json.loads(urlopen(statsapi_url).read().decode('utf_8'))
	api_game_id = statsapi_data['game_id']
	game_year = api_game_id.split("/")[0]
	game_month = api_game_id.split("/")[1]
	game_date = api_game_id.split("/")[2]
	game_matchup = api_game_id.split("/")[3].replace("-","_")
	pfx_url = "http://gd2.mlb.com/components/game/mlb/year_"+game_year+"/month_"+game_month+"/day_"+game_date+"/gid_"+game_year+"_"+game_month+"_"+game_date+"_"+game_matchup+"/inning/inning_all.xml"
	pfx_data = BeautifulSoup(urlopen(pfx_url), "xml")
	play_guid_list = []
	for pitch in pfx_data.find_all('pitch'):
		if 'play_guid' in pitch.attrs:
			if pitch['play_guid'] not in play_guid_list:
				play_guid_list.append(pitch['play_guid'])
	#live file section
	live_filelist = []
	for f in BeautifulSoup(urlopen("http://gd2.mlb.com/components/game/play-builder/"+game+"/live/")).find_all('a', href=re.compile('.*json')):
		if f.get_text().strip()[0:f.get_text().strip().find("_")] in play_guid_list:
			live_filelist.append(game+"/live/"+f.get_text().strip())
	lf = 0
	cwd = os.getcwd()
	if sys.platform=='linux':
		if not os.path.isdir(cwd+"/ball_tracking"):
			os.mkdir(cwd+"/ball_tracking")
		if not os.path.isdir(cwd+"/live_file_data"):
			os.mkdir(cwd+"/live_file_data")
	elif sys.platform=='win64' or sys.platform=='win32':
		if not os.path.isdir(cwd+"\\ball_tracking"):
			os.mkdir(cwd+"\\ball_tracking")
		if not os.path.isdir(cwd+"\\live_file_data"):
			os.mkdir(cwd+"\\live_file_data")
	else:
		print("OS not recognized; check source code and modify as necessary for compatibility")
		quit()
	for i in live_filelist:
		lf+=1
		print("running live file "+str(lf)+" of "+str(len(live_filelist)))
		fileurl = urlbase+i
		data = json.loads(urlopen(fileurl).read().decode('utf_8'))
		id = i[12:i.find("_")]
		for package in data['pkgs']:
			if package['typ']=='0':
				os.chdir("live_file_data")
				typ0_outfile = open("typ0_data.csv", "a+")
				if os.stat("typ0_data.csv").st_size==0:
					typ0_outfile.write("play_guid,release_speed\n")
				rs = str(package['data']['PitchReleaseData']['ReleaseSpeed'])
				typ0_outfile.write(id+","+rs+"\n")
				typ0_outfile.close()
				os.chdir("..")
			elif package['typ']=='1':
				os.chdir("live_file_data")
				typ1_t_outfile = open("typ1_trajectory_data.csv", "a+")
				typ1_r_outfile = open("typ1_release_data.csv", "a+")
				if os.stat("typ1_trajectory_data.csv").st_size==0:
					typ1_t_outfile.write("play_guid,zone_speed,zone_time,effective_velocity,loc_x,loc_y,loc_z,traj_poly_x1,traj_poly_x2,traj_poly_x3,traj_poly_y1,traj_poly_y2,traj_poly_y3,traj_poly_z1,traj_poly_z2,traj_poly_z3,horiz_approach_angle,vert_approach_angle,horiz_break,vert_break,vert_break_induced\n")
				if os.stat("typ1_release_data.csv").st_size==0:
					typ1_r_outfile.write("play_guid,release_angle,release_speed,pos_x,pos_y,pos_z,spin_axis,extension,direction\n")
				zs = str(package['data']['LivePitchData']['TrajectoryData']['ZoneSpeed'])
				zt = str(package['data']['LivePitchData']['TrajectoryData']['ZoneTime'])
				ev = str(package['data']['LivePitchData']['TrajectoryData']['EffectiveVelocity'])
				loc_x = str(package['data']['LivePitchData']['TrajectoryData']['Location']['X'])
				loc_y = str(package['data']['LivePitchData']['TrajectoryData']['Location']['Y'])
				loc_z = str(package['data']['LivePitchData']['TrajectoryData']['Location']['Z'])
				traj_poly_x1 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialX'][0])
				traj_poly_x2 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialX'][1])
				traj_poly_x3 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialX'][2])
				traj_poly_y1 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialY'][0])
				traj_poly_y2 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialY'][1])
				traj_poly_y3 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialY'][2])
				traj_poly_z1 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialZ'][0])
				traj_poly_z2 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialZ'][1])
				traj_poly_z3 = loc_x = str(package['data']['LivePitchData']['TrajectoryData']['TrajectoryPolynomialZ'][2])
				haa = str(package['data']['LivePitchData']['TrajectoryData']['HorizontalApproachAngle'])
				vaa = str(package['data']['LivePitchData']['TrajectoryData']['VerticalApproachAngle'])
				hb = str(package['data']['LivePitchData']['TrajectoryData']['HorizontalBreak'])
				vb = str(package['data']['LivePitchData']['TrajectoryData']['VerticalBreak'])
				vbi = hb = str(package['data']['LivePitchData']['TrajectoryData']['VerticalBreakInduced'])
				typ1_t_outfile.write(id+","+zs+","+zt+","+ev+","+loc_x+","+loc_y+","+loc_z+","+traj_poly_x1+","+traj_poly_x2+","+traj_poly_x3+","+traj_poly_y1+","+traj_poly_y2+","+traj_poly_y3+","+traj_poly_z1+","+traj_poly_z2+","+traj_poly_z3+","+haa+","+vaa+","+hb+","+vb+","+vbi+"\n")
				typ1_t_outfile.close()
				ra = str(package['data']['LivePitchData']['ReleaseData']['Angle'])
				rs = str(package['data']['LivePitchData']['ReleaseData']['ReleaseSpeed'])
				px = str(package['data']['LivePitchData']['ReleaseData']['ReleasePosition']['X'])
				py = str(package['data']['LivePitchData']['ReleaseData']['ReleasePosition']['Y'])
				pz = str(package['data']['LivePitchData']['ReleaseData']['ReleasePosition']['Z'])
				sa = str(package['data']['LivePitchData']['ReleaseData']['SpinAxis'])
				ext = str(package['data']['LivePitchData']['ReleaseData']['Extension'])
				d = str(package['data']['LivePitchData']['ReleaseData']['Direction'])
				typ1_r_outfile.write(id+","+ra+","+rs+","+px+","+py+","+pz+","+sa+","+ext+","+d+"\n")
				typ1_r_outfile.close()
				os.chdir("..")
			elif package['typ']==2:
				os.chdir("ball_tracking")
				pitchout_filename = "pitchtrack_"+str(id)+".csv"
				pitchout = open(pitchout_filename, "a+")
				if os.stat(pitchout_filename).st_size==0:
					pitchout.write("playID,Time,TimeCode,TimeCodeOffset,pos_x,pos_y,pos_z,velo_x,velo_y,velo_z\n")
				for pos in package['data']['LiveTrajectoryData']['BallPositions']:
					time = pos['BallPosition']['Time']
					timecode = pos['BallPosition']['TimeCode']
					tco = pos['BallPosition']['TimeCodeOffset']
					pos_x = pos['BallPosition']['Position']['X']
					pos_y = pos['BallPosition']['Position']['Y']
					pos_z = pos['BallPosition']['Position']['Z']
					vel_x = pos['BallPosition']['Velocity']['X']
					vel_y = pos['BallPosition']['Velocity']['Y']
					vel_z = pos['BallPosition']['Velocity']['Z']
					pitchout.write(id+","+str(time)+","+str(timecode)+","+str(tco)+","+str(pos_x)+","+str(pos_y)+","+str(pos_z)+","+str(vel_x)+","+str(vel_y)+","+str(vel_z)+"\n")
				pitchout.close()
				os.chdir("..")
			elif package['typ']==4:
				os.chdir("live_file_data")
				typ4_t_outfile = open("typ4_pitch_trajectory_data.csv", "a+")
				typ4_r_outfile = open("typ4_pitch_release_data.csv", "a+")
				typ4_m_outfile = open("typ4_pitch_measurement_data.csv", "a+")
				if os.stat("typ4_pitch_trajectory_data.csv").st_size==0:
					typ4_t_outfile.write("play_guid,zone_speed,zone_time,effective_velocity,loc_x,loc_y,loc_z,traj_poly_x1,traj_poly_x2,traj_poly_x3,traj_poly_y1,traj_poly_y2,traj_poly_y3,traj_poly_z1,traj_poly_z2,traj_poly_z3,horiz_approach_angle,vert_approach_angle,horiz_break,vert_break,vert_break_induced\n")
				if os.stat("typ4_pitch_release_data.csv").st_size==0:
					typ4_r_outfile.write("play_guid,release_angle,release_speed,pos_x,pos_y,pos_z,spin_axis,spin_rate,extension,direction\n")
				if os.stat("typ4_pitch_measurement_data.csv").st_size==0:
					typ4_m_outfile.write("play_guid,time,distance,bearing,pos_x,pos_y,pos_z,velo_x,velo_y,velo_z\n")
				if 'PitchSegment' in package['data']['Measurement']:
					zs = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['ZoneSpeed'])
					zt = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['ZoneTime'])
					ev = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['EffectiveVelocity'])
					loc_x = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['Location']['X'])
					loc_y = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['Location']['Y'])
					loc_z = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['Location']['Z'])
					traj_poly_x1 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialX'][0])
					traj_poly_x2 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialX'][1])
					traj_poly_x3 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialX'][2])
					traj_poly_y1 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialY'][0])
					traj_poly_y2 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialY'][1])
					traj_poly_y3 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialY'][2])
					traj_poly_z1 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialZ'][0])
					traj_poly_z2 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialZ'][1])
					traj_poly_z3 = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['TrajectoryPolynomialZ'][2])
					haa = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['HorizontalApproachAngle'])
					vaa = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['VerticalApproachAngle'])
					hb = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['HorizontalBreak'])
					vb = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['VerticalBreak'])
					vbi = hb = str(package['data']['Measurement']['PitchSegment']['TrajectoryData']['VerticalBreakInduced'])
					typ4_t_outfile.write(id+","+zs+","+zt+","+ev+","+loc_x+","+loc_y+","+loc_z+","+traj_poly_x1+","+traj_poly_x2+","+traj_poly_x3+","+traj_poly_y1+","+traj_poly_y2+","+traj_poly_y3+","+traj_poly_z1+","+traj_poly_z2+","+traj_poly_z3+","+haa+","+vaa+","+hb+","+vb+","+vbi+"\n")
					typ4_t_outfile.close()
					ra = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['Angle'])
					rs = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['ReleaseSpeed'])
					px = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['ReleasePosition']['X'])
					py = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['ReleasePosition']['Y'])
					pz = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['ReleasePosition']['Z'])
					sa = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['SpinAxis']) if 'SpinAxis' in package['data']['Measurement']['PitchSegment']['ReleaseData'] else "NULL"
					ext = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['Extension'])
					d = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['Direction'])
					sr = str(package['data']['Measurement']['PitchSegment']['ReleaseData']['SpinRate']) if 'SpinRate' in package['data']['Measurement']['PitchSegment']['ReleaseData'] else "NULL"
					typ4_r_outfile.write(id+","+ra+","+rs+","+px+","+py+","+pz+","+sa+","+sr+","+ext+","+d+"\n")
					typ4_r_outfile.close()
					lmtime = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Time'])
					lmdistance = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Distance'])
					lmbearing = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Bearing'])
					lm_px = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Position']['X'])
					lm_py = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Position']['Y'])
					lm_pz = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Position']['Z'])
					lm_vx = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Velocity']['X'])
					lm_vy = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Velocity']['Y'])
					lm_vz = str(package['data']['Measurement']['PitchSegment']['LastMeasuredData']['Velocity']['Z'])
					typ4_m_outfile.write(id+","+lmtime+","+lmdistance+","+lmbearing+","+lm_px+","+lm_py+","+lm_pz+","+lm_vx+","+lm_vy+","+lm_vz+"\n")
					typ4_m_outfile.close()
				for s in package['data']['Measurement']['Segments']:
					if s['SegmentData']['SegmentType']=="BaseballPitch":
						pitchsegment_out = open("typ4_pitchsegments.csv", "a+")
						if os.stat("typ4_pitchsegments.csv").st_size==0:
							pitchsegment_out.write("play_guid,start_time_start_speed,start_pos_x,start_pos_y,start_pos_z,start_velo_x,start_velo_y,start_velo_z,end_time,end_speed,end_pos_x,end_pos_y,end_pos_z,end_velo_x,end_velo_y,end_velo_x,end_velo_y,end_velo_z,landing_time,landing_pos_x,landing_pos_y,landing_pos_z,traj_poly_x1,traj_poly_x2,traj_poly_x3,traj_poly_y1,traj_poly_y2,traj_poly_y3,traj_poly_z1,traj_poly_z2,traj_poly_z3\n")
						st = str(s['SegmentData']['StartData']['Time'])
						ss = str(s['SegmentData']['StartData']['Speed'])
						spx = str(s['SegmentData']['StartData']['Position']['X'])
						spy = str(s['SegmentData']['StartData']['Position']['Y'])
						spz = str(s['SegmentData']['StartData']['Position']['Z'])
						svx = str(s['SegmentData']['StartData']['Velocity']['X'])
						svy = str(s['SegmentData']['StartData']['Velocity']['Y'])
						svz = str(s['SegmentData']['StartData']['Velocity']['Z'])
						et = str(s['SegmentData']['EndData']['Time'])
						es = str(s['SegmentData']['EndData']['Speed'])
						epx = str(s['SegmentData']['EndData']['Position']['X'])
						epy = str(s['SegmentData']['EndData']['Position']['Y'])
						epz = str(s['SegmentData']['EndData']['Position']['Z'])
						evx = str(s['SegmentData']['EndData']['Velocity']['X'])
						evy = str(s['SegmentData']['EndData']['Velocity']['Y'])
						evz = str(s['SegmentData']['EndData']['Velocity']['Z'])
						lt = str(s['SegmentData']['LandingData']['Time'])
						lpx = str(s['SegmentData']['LandingData']['Position']['X'])
						lpy = str(s['SegmentData']['LandingData']['Position']['Y'])
						lpz = str(s['SegmentData']['LandingData']['Position']['Z'])
						traj_poly_x1 = str(s['SegmentData']['TrajectoryPolynomialX'][0])
						traj_poly_x2 = str(s['SegmentData']['TrajectoryPolynomialX'][1])
						traj_poly_x3 = str(s['SegmentData']['TrajectoryPolynomialX'][2])
						traj_poly_y1 = str(s['SegmentData']['TrajectoryPolynomialY'][0])
						traj_poly_y2 = str(s['SegmentData']['TrajectoryPolynomialY'][1])
						traj_poly_y3 = str(s['SegmentData']['TrajectoryPolynomialY'][2])
						traj_poly_z1 = str(s['SegmentData']['TrajectoryPolynomialZ'][0])
						traj_poly_z2 = str(s['SegmentData']['TrajectoryPolynomialZ'][1])
						traj_poly_z3 = str(s['SegmentData']['TrajectoryPolynomialZ'][2])
						pitchsegment_out.write(id+","+st+","+ss+","+spx+","+spy+","+spz+","+svx+","+svy+","+svz+","+et+","+es+","+epx+","+epy+","+epz+","+evx+","+evy+","+evz+","+lt+","+lpx+","+lpy+","+lpz+","+traj_poly_x1+","+traj_poly_x2+","+traj_poly_x3+","+traj_poly_y1+","+traj_poly_y2+","+traj_poly_y3+","+traj_poly_z1+","+traj_poly_z2+","+traj_poly_z3+"\n")
						pitchsegment_out.close()
					elif s['SegmentData']['SegmentType']=="BaseballDeflection":
						defsegment_out = open("typ4_deflectionsegments.csv", "a+")
						if os.stat("typ4_deflectionsegments.csv").st_size==0:
							defsegment_out.write("play_guid,start_time_start_speed,start_pos_x,start_pos_y,start_pos_z,start_velo_x,start_velo_y,start_velo_z,end_time,end_speed,end_pos_x,end_pos_y,end_pos_z,end_velo_x,end_velo_y,end_velo_x,end_velo_y,end_velo_z,landing_time,landing_pos_x,landing_pos_y,landing_pos_z,traj_poly_x1,traj_poly_x2,traj_poly_x3,traj_poly_y1,traj_poly_y2,traj_poly_y3,traj_poly_z1,traj_poly_z2,traj_poly_z3\n")
						st = str(s['SegmentData']['StartData']['Time'])
						ss = str(s['SegmentData']['StartData']['Speed'])
						spx = str(s['SegmentData']['StartData']['Position']['X'])
						spy = str(s['SegmentData']['StartData']['Position']['Y'])
						spz = str(s['SegmentData']['StartData']['Position']['Z'])
						svx = str(s['SegmentData']['StartData']['Velocity']['X'])
						svy = str(s['SegmentData']['StartData']['Velocity']['Y'])
						svz = str(s['SegmentData']['StartData']['Velocity']['Z'])
						et = str(s['SegmentData']['EndData']['Time'])
						es = str(s['SegmentData']['EndData']['Speed'])
						epx = str(s['SegmentData']['EndData']['Position']['X'])
						epy = str(s['SegmentData']['EndData']['Position']['Y'])
						epz = str(s['SegmentData']['EndData']['Position']['Z'])
						evx = str(s['SegmentData']['EndData']['Velocity']['X'])
						evy = str(s['SegmentData']['EndData']['Velocity']['Y'])
						evz = str(s['SegmentData']['EndData']['Velocity']['Z'])
						lt = str(s['SegmentData']['LandingData']['Time'])
						lpx = str(s['SegmentData']['LandingData']['Position']['X'])
						lpy = str(s['SegmentData']['LandingData']['Position']['Y'])
						lpz = str(s['SegmentData']['LandingData']['Position']['Z'])
						traj_poly_x1 = str(s['SegmentData']['TrajectoryPolynomialX'][0])
						traj_poly_x2 = str(s['SegmentData']['TrajectoryPolynomialX'][1])
						traj_poly_x3 = str(s['SegmentData']['TrajectoryPolynomialX'][2])
						traj_poly_y1 = str(s['SegmentData']['TrajectoryPolynomialY'][0])
						traj_poly_y2 = str(s['SegmentData']['TrajectoryPolynomialY'][1])
						traj_poly_y3 = str(s['SegmentData']['TrajectoryPolynomialY'][2])
						traj_poly_z1 = str(s['SegmentData']['TrajectoryPolynomialZ'][0])
						traj_poly_z2 = str(s['SegmentData']['TrajectoryPolynomialZ'][1])
						traj_poly_z3 = str(s['SegmentData']['TrajectoryPolynomialZ'][2])
						defsegment_out.write(id+","+st+","+ss+","+spx+","+spy+","+spz+","+svx+","+svy+","+svz+","+et+","+es+","+epx+","+epy+","+epz+","+evx+","+evy+","+evz+","+lt+","+lpx+","+lpy+","+lpz+","+traj_poly_x1+","+traj_poly_x2+","+traj_poly_x3+","+traj_poly_y1+","+traj_poly_y2+","+traj_poly_y3+","+traj_poly_z1+","+traj_poly_z2+","+traj_poly_z3+"\n")
						defsegment_out.close()
					else:
						unk_seg_out = open("typ4_othersegments.csv", "a+")
						if os.stat("typ4_othersegments.csv").st_size==0:
							unk_seg_out.write("play_guid,segment_type,start_time_start_speed,start_pos_x,start_pos_y,start_pos_z,start_velo_x,start_velo_y,start_velo_z,end_time,end_speed,end_pos_x,end_pos_y,end_pos_z,end_velo_x,end_velo_y,end_velo_x,end_velo_y,end_velo_z,landing_time,landing_pos_x,landing_pos_y,landing_pos_z,traj_poly_x1,traj_poly_x2,traj_poly_x3,traj_poly_y1,traj_poly_y2,traj_poly_y3,traj_poly_z1,traj_poly_z2,traj_poly_z3\n")
						segtyp = s['SegmentData']['SegmentType']
						st = str(s['SegmentData']['StartData']['Time'])
						ss = str(s['SegmentData']['StartData']['Speed'])
						spx = str(s['SegmentData']['StartData']['Position']['X'])
						spy = str(s['SegmentData']['StartData']['Position']['Y'])
						spz = str(s['SegmentData']['StartData']['Position']['Z'])
						svx = str(s['SegmentData']['StartData']['Velocity']['X'])
						svy = str(s['SegmentData']['StartData']['Velocity']['Y'])
						svz = str(s['SegmentData']['StartData']['Velocity']['Z'])
						et = str(s['SegmentData']['EndData']['Time'])
						es = str(s['SegmentData']['EndData']['Speed'])
						epx = str(s['SegmentData']['EndData']['Position']['X'])
						epy = str(s['SegmentData']['EndData']['Position']['Y'])
						epz = str(s['SegmentData']['EndData']['Position']['Z'])
						evx = str(s['SegmentData']['EndData']['Velocity']['X'])
						evy = str(s['SegmentData']['EndData']['Velocity']['Y'])
						evz = str(s['SegmentData']['EndData']['Velocity']['Z'])
						lt = str(s['SegmentData']['LandingData']['Time'])
						lpx = str(s['SegmentData']['LandingData']['Position']['X'])
						lpy = str(s['SegmentData']['LandingData']['Position']['Y'])
						lpz = str(s['SegmentData']['LandingData']['Position']['Z'])
						traj_poly_x1 = str(s['SegmentData']['TrajectoryPolynomialX'][0])
						traj_poly_x2 = str(s['SegmentData']['TrajectoryPolynomialX'][1])
						traj_poly_x3 = str(s['SegmentData']['TrajectoryPolynomialX'][2])
						traj_poly_y1 = str(s['SegmentData']['TrajectoryPolynomialY'][0])
						traj_poly_y2 = str(s['SegmentData']['TrajectoryPolynomialY'][1])
						traj_poly_y3 = str(s['SegmentData']['TrajectoryPolynomialY'][2])
						traj_poly_z1 = str(s['SegmentData']['TrajectoryPolynomialZ'][0])
						traj_poly_z2 = str(s['SegmentData']['TrajectoryPolynomialZ'][1])
						traj_poly_z3 = str(s['SegmentData']['TrajectoryPolynomialZ'][2])
						unk_seg_out.write(id+","+segtyp+","+st+","+ss+","+spx+","+spy+","+spz+","+svx+","+svy+","+svz+","+et+","+es+","+epx+","+epy+","+epz+","+evx+","+evy+","+evz+","+lt+","+lpx+","+lpy+","+lpz+","+traj_poly_x1+","+traj_poly_x2+","+traj_poly_x3+","+traj_poly_y1+","+traj_poly_y2+","+traj_poly_y3+","+traj_poly_z1+","+traj_poly_z2+","+traj_poly_z3+"\n")
						unk_seg_out.close()
				os.chdir("..")
			elif package['typ']==7:
				os.chdir("live_file_data")
				typ7_out = open("typ7_playinfo.csv", "a+")
				if os.stat("typ7_playinfo.csv").st_size==0:
					typ7_out.write("play_guid,pos_id,event_id]\n")
				pos_id = str(package['data']['PlayEventData']['positionID'])
				event_id = str(package['data']['PlayEventData']['playEventType'])
				typ7_out.write(id+","+pos_id+","+event_id+"\n")
				typ7_out.close()
				os.chdir("..")
			elif package['typ']==8:
				os.chdir("live_file_data")
				typ8file = open("typ8_metadata.csv","a+")
				if os.stat("typ8_metadata.csv").st_size==0:
					typ8file.write("id,game,venue_id,inning,inning_half,ab_number,pitch_number,bat_id,bat_hand_cd,pit_id,pit_hand_cd,fdest\n")
				ab_number = package['data']['FAtBatNumber']
				pitch_number = package['data']['FPitchNumber']
				pit_hand_cd = package['data']['FThrows']
				bat_hand_cd = package['data']['FStance']
				inning = package['data']['FInning']
				bat_id = package['data']['FBatterID']
				pit_id = package['data']['FPitcherID']
				if package['data']['FTopInningSwitch'] == "true":
					inning_half = 0
				else:
					inning_half = 1
				fdest = package['data']['FDestination']
				venue_id = package['data']['FVenueID']
				typ8file.write(str(id)+","+str(game)+","+str(venue_id)+","+str(inning)+","+str(inning_half)+","+str(ab_number)+","+str(pitch_number)+","+str(bat_id)+","+str(bat_hand_cd)+","+str(pit_id)+","+str(pit_hand_cd)+","+str(fdest)+"\n")
				typ8file.close()
				os.chdir("..")
	#event file section
	event_filelist = []
	try:
		for f in BeautifulSoup(urlopen("http://gd2.mlb.com/components/game/play-builder/"+game+"/event/")).find_all('a', href=re.compile('.*json')):
			if f.get_text().strip()[0:f.get_text().strip().find("_")] in play_guid_list:
				event_filelist.append(f.get_text().strip())
	except:
		continue
	ef = 0
	completed_event_list = []
	for i in event_filelist:
		ef+=1
		print("running event file "+str(ef))
		fileurl = "http://gd2.mlb.com/components/game/play-builder/"+game+"/event/"+i
		data = json.loads(urlopen(fileurl).read().decode('utf_8'))
		id = i[0:i.find("_")]
		if id not in completed_event_list:
			completed_event_list.append(id)
			event_out = open("playerids_by_play.csv", "a+")
			if os.stat("playerids_by_play.csv").st_size==0:
				event_out.write("gpk,play_guid,pos1_id,pos2_id,pos3_id,pos4_id,pos5_id,pos6_id,pos7_id,pos8_id,pos9_id,pos10_id,pos11_id,pos12_id,pos13_id,pos14_id,pos15_id,pos16_id,pos17_id,pos18_id,pos19_id,event_type,inning,inning_half,outs,balls,strikes\n")
			gpk = data['gpk']
			guid = data['guid']
			pos1_id = data['lineup'][0]['id']
			pos2_id = data['lineup'][1]['id']
			pos3_id = data['lineup'][2]['id']
			pos4_id = data['lineup'][3]['id']
			pos5_id = data['lineup'][4]['id']
			pos6_id = data['lineup'][5]['id']
			pos7_id = data['lineup'][6]['id']
			pos8_id = data['lineup'][7]['id']
			pos9_id = data['lineup'][8]['id']
			pos10_id = data['lineup'][9]['id']
			pos11_id = data['lineup'][10]['id']
			pos12_id = data['lineup'][11]['id']
			pos13_id = data['lineup'][12]['id']
			pos14_id = data['umpires'][0]['id']
			pos15_id = data['umpires'][1]['id']
			pos16_id = data['umpires'][2]['id']
			pos17_id = data['umpires'][3]['id']
			pos18_id = data['umpires'][4]['id']
			pos19_id = data['umpires'][5]['id']
			event_type = data['event'][0]['typ']
			inning = data['sit']['inning']
			inning_half = data['sit']['top_inning']
			outs = data['sit']['outs']
			balls = data['sit']['balls']
			strikes = data['sit']['strikes']
			event_out.write(str(gpk)+","+str(guid)+","+str(pos1_id)+","+str(pos2_id)+","+str(pos3_id)+","+str(pos4_id)+","+str(pos5_id)+","+str(pos6_id)+","+str(pos7_id)+","+str(pos8_id)+","+str(pos9_id)+","+str(pos10_id)+","+str(pos11_id)+","+str(pos12_id)+","+str(pos13_id)+","+str(pos14_id)+","+str(pos15_id)+","+str(pos16_id)+","+str(pos17_id)+","+str(pos18_id)+","+str(pos19_id)+","+str(event_type)+","+str(inning)+","+str(inning_half)+","+str(outs)+","+str(balls)+","+str(strikes)+"\n")
  #refined file section
	refined_filelist = []
	for f in BeautifulSoup(urlopen("http://gd2.mlb.com/components/game/play-builder/"+game+"/refined/")).find_all('a', href=re.compile('.*json')):
		if f.get_text().strip()[0:f.get_text().strip().find("_")] in play_guid_list:
			refined_filelist.append(f.get_text().strip())
	rf = 0
	for i in refined_filelist:
		rf += 1
		print("running refined file "+str(rf)+" of "+str(len(refined_filelist)))
		fileurl = urlbase+game+"/refined/"+i
		data = json.loads(urlopen(fileurl).read().decode('utf_8'))
		id = i[0:i.find("_")]
		rf_out = open("player_tracker.csv", "a+")
		if os.stat("player_tracker.csv").st_size==0:
			rf_out.write("play_guid,timestamp,gpk,pos1_x,pos1_y,pos2_x,pos2_y,pos3_x,pos3_y,pos4_x,pos4_y,pos5_x,pos5_y,pos6_x,pos6_y,pos7_x,pos7_y,pos8_x,pos8_y,pos9_x,pos9_y,bat_x,bat_y,run1_x,run1_y,run2_x,run2_y,run3_x,run3_y,ump1_x,ump1_y,ump2_x,ump2_y,ump3_x,ump3_y,ump4_x,ump4_y,ump5_x,ump5_y,ump6_x,ump6_y,ball_x,ball_y,ball_z\n")
		timestamp = data['fts']
		gpk = data['gpk']
		pos1_x = "NULL"
		pos1_y = "NULL"
		pos2_x = "NULL"
		pos2_y = "NULL"
		pos3_x = "NULL"
		pos3_y = "NULL"
		pos4_x = "NULL"
		pos4_y = "NULL"
		pos5_x = "NULL"
		pos5_y = "NULL"
		pos6_x = "NULL"
		pos6_y = "NULL"
		pos7_x = "NULL"
		pos7_y = "NULL"
		pos8_x = "NULL"
		pos8_y = "NULL"
		pos9_x = "NULL"
		pos9_y = "NULL"
		bat_x = "NULL"
		bat_y = "NULL"
		run1_x = "NULL"
		run1_y = "NULL"
		run2_x = "NULL"
		run2_y = "NULL"
		run3_x = "NULL"
		run3_y = "NULL"
		ump1_x = "NULL"
		ump1_y = "NULL"
		ump2_x = "NULL"
		ump2_y = "NULL"
		ump3_x = "NULL"
		ump3_y = "NULL"
		ump4_x = "NULL"
		ump4_y = "NULL"
		ump5_x = "NULL"
		ump5_y = "NULL"
		ump6_x = "NULL"
		ump6_y = "NULL"
		ball_x = "NULL"
		ball_y = "NULL"
		ball_z = "NULL"
		for item in data['trgts']:
			if item['typ']==1:
				if item.get('id'):
					if item['id']==1:
						pos1_x=item['x']
						pos1_y=item['y']
					if item['id']==2:
						pos2_x=item['x']
						pos2_y=item['y']
					if item['id']==3:
						pos3_x=item['x']
						pos3_y=item['y']
					if item['id']==4:
						pos4_x=item['x']
						pos4_y=item['y']
					if item['id']==5:
						pos5_x=item['x']
						pos5_y=item['y']
					if item['id']==6:
						pos6_x=item['x']
						pos6_y=item['y']
					if item['id']==7:
						pos7_x=item['x']
						pos7_y=item['y']
					if item['id']==8:
						pos8_x=item['x']
						pos8_y=item['y']
					if item['id']==9:
						pos9_x=item['x']
						pos9_y=item['y']
					if item['id']==10:
						bat_x=item['x']
						bat_y=item['y']
					if item['id']==11:
						run1_x=item['x']
						run1_y=item['y']
					if item['id']==12:
						run2_x=item['x']
						run2_y=item['y']
					if item['id']==13:
						run3_x=item['x']
						run3_y=item['y']
			if item['typ']==2:
				if item.get('id'):
					if item['id']==14:
						ump1_x = item['x']
						ump1_y = item['y']
					if item['id']==15:
						ump2_x = item['x']
						ump2_y = item['y']
					if item['id']==16:
						ump3_x = item['x']
						ump3_y = item['y']
					if item['id']==17:
						ump4_x = item['x']
						ump4_y = item['y']
					if item['id']==18:
						ump5_x = item['x']
						ump5_y = item['y']
					if item['id']==19:
						ump6_x = item['x']
						ump6_y = item['y']
			if item['typ']==4:
				ball_x = item['x']
				ball_y = item['y']
				ball_z = item['z']
		rf_out.write(str(timestamp)+","+str(gpk)+","+id+","+str(pos1_x)+","+str(pos1_y)+","+str(pos2_x)+","+str(pos2_y)+","+str(pos3_x)+","+str(pos3_y)+","+str(pos4_x)+","+str(pos4_y)+","+str(pos5_x)+","+str(pos5_y)+","+str(pos6_x)+","+str(pos6_y)+","+str(pos7_x)+","+str(pos7_y)+","+str(pos8_x)+","+str(pos8_y)+","+str(pos9_x)+","+str(pos9_y)+","+str(bat_x)+","+str(bat_y)+","+str(run1_x)+","+str(run1_y)+","+str(run2_x)+","+str(run2_y)+","+str(run3_x)+","+str(run3_y)+","+str(ump1_x)+","+str(ump1_y)+","+str(ump2_x)+","+str(ump2_y)+","+str(ump3_x)+","+str(ump3_y)+","+str(ump4_x)+","+str(ump4_y)+","+str(ump5_x)+","+str(ump5_y)+","+str(ump6_x)+","+str(ump6_y)+","+str(ball_x)+","+str(ball_y)+","+str(ball_z)+"\n")
	os.chdir("..")