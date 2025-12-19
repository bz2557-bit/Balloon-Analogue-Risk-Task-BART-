#BART (Balloon Analogue Risk Task) with balloon types (Safe vs Risky)

from psychopy import visual, core, event, gui
import random
import os
import csv
from datetime import datetime


#Settings

N_BALLOONS = 30

#Balloon-type manipulation
SHOW_TYPE_CUE = True
P_SAFE = 0.5  #proportion of safe balloons

#Explosion thresholds by type
SAFE_THRESH_MIN, SAFE_THRESH_MAX = 18, 40      #safer=higher threshold
RISKY_THRESH_MIN, RISKY_THRESH_MAX = 5, 22     #riskier=lower threshold

#Reward schedule (safe=slower, risky=faster)
SAFE_BASE_GAIN, SAFE_GAIN_STEP, SAFE_MAX_GAIN = 1, 4, 5
RISKY_BASE_GAIN, RISKY_GAIN_STEP, RISKY_MAX_GAIN = 1, 2, 6

BALLOON_START_RADIUS = 0.06
BALLOON_RADIUS_STEP  = 0.01

FIX_FEEDBACK_DUR = 0.5
ITI = 0.4

QUIT_KEY = 'escape'


def ensure_data_folder():
    folder = os.path.join(os.getcwd(), "data")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def save_rows_to_csv(rows, out_path):
    if len(rows) == 0:
        return
    keys = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def gain_for_pump(pump_number, base_gain, gain_step, max_gain):
    gain = base_gain + (pump_number - 1) // gain_step
    if gain > max_gain:
        gain = max_gain
    return gain


def main():
    info = {"participant": "P001", "session": "001"}
    dlg = gui.DlgFromDict(info, title="BART Task")
    if not dlg.OK:
        return


    balloon_types = []
    thresholds = []
    reward_params = [] 

    for i in range(N_BALLOONS):
        btype = "safe" if random.random() < P_SAFE else "risky"
        balloon_types.append(btype)

        if btype == "safe":
            thresholds.append(random.randint(SAFE_THRESH_MIN, SAFE_THRESH_MAX))
            reward_params.append((SAFE_BASE_GAIN, SAFE_GAIN_STEP, SAFE_MAX_GAIN))
        else:
            thresholds.append(random.randint(RISKY_THRESH_MIN, RISKY_THRESH_MAX))
            reward_params.append((RISKY_BASE_GAIN, RISKY_GAIN_STEP, RISKY_MAX_GAIN))


    win = visual.Window(size=(1100, 750), color="black", units="norm", fullscr=False)

    title = visual.TextStim(
        win,
        text="BART (Balloon Analogue Risk Task)",
        height=0.06,
        color="white",
        pos=(0, 0.78)
    )


    instructions = visual.TextStim(
        win,
        text=(
            "Instructions\n\n"
            "In this task, you will see a balloon on the screen.\n"
            "Press SPACE to pump the balloon. Each pump increases the points for the current balloon.\n"
            "Press ENTER to COLLECT the current balloon points into your final score.\n\n"
            "The balloon can explode at an unknown time.\n"
            "If it explodes before you collect, you lose ALL points for that balloon.\n\n"
            "Balloon types:\n"
            "- GREEN balloons are safer (less likely to explode) but points grow more slowly.\n"
            "- RED balloons are riskier (more likely to explode) but points grow faster.\n\n"
            "Try to earn as many points as possible!\n\n"
            "Press SPACE to start.\n"
            f"Press {QUIT_KEY.upper()} to quit anytime."
        ),
        height=0.055,
        color="white",
        wrapWidth=1.75,
        pos=(0, 0.12),
    )

    run_text = visual.TextStim(win, text="", height=0.06, color="white", pos=(-0.78, 0.65))

    hint_text = visual.TextStim(
        win,
        text="SPACE = pump   |   ENTER = collect",
        height=0.04,
        color="white",
        pos=(0, -0.90)
    )

    feedback = visual.TextStim(win, text="", height=0.08, color="white", pos=(0, 0))

    #Balloon
    balloon = visual.Circle(
        win,
        radius=BALLOON_START_RADIUS,
        fillColor="red",
        lineColor="red",
        edges=128,
        pos=(0, 0.05),
    )

    knot = visual.Polygon(
        win,
        edges=3,
        radius=0.02,
        fillColor="red",
        lineColor="red",
        pos=(0, balloon.pos[1] - BALLOON_START_RADIUS - 0.02),
        ori=180,
    )

    string = visual.Line(
        win,
        start=(0, knot.pos[1] - 0.02),
        end=(0, knot.pos[1] - 0.25),
        lineColor="white",
        lineWidth=2,
    )

    #Start screen
    title.draw()
    instructions.draw()
    win.flip()
    k = event.waitKeys(keyList=["space", QUIT_KEY])
    if QUIT_KEY in k:
        win.close()
        return

    #Data storage
    rows = []
    global_clock = core.Clock()
    total_points = 0

    try:
        for b in range(1, N_BALLOONS + 1):
            thresh = thresholds[b - 1]
            btype = balloon_types[b - 1]
            base_gain, gain_step, max_gain = reward_params[b - 1]

            pumps = 0
            temp_points = 0

            # Set balloon appearance based on type (VISIBLE cue)
            if SHOW_TYPE_CUE:
                if btype == "safe":
                    balloon.fillColor = "green"
                    balloon.lineColor = "green"
                    knot.fillColor = "green"
                    knot.lineColor = "green"
                else:
                    balloon.fillColor = "red"
                    balloon.lineColor = "red"
                    knot.fillColor = "red"
                    knot.lineColor = "red"


            balloon.radius = BALLOON_START_RADIUS


            knot.pos = (0, balloon.pos[1] - balloon.radius - 0.02)
            string.start = (0, knot.pos[1] - 0.02)
            string.end   = (0, knot.pos[1] - 0.25)

            while True:
                title.draw()

                run_text.text = "Points for this run: %d" % temp_points
                run_text.draw()
                hint_text.draw()

                balloon.draw()
                knot.draw()
                string.draw()

                win.flip()

                keys = event.waitKeys(keyList=["space", "return", "enter", QUIT_KEY])
                t = global_clock.getTime()

                if QUIT_KEY in keys:
                    raise KeyboardInterrupt()

                #Pump
                if "space" in keys:
                    pumps += 1

                    #Explode
                    if pumps > thresh:
                        temp_points = 0

                        rows.append({
                            "participant": info["participant"],
                            "session": info["session"],
                            "balloon": b,
                            "balloon_type": btype,
                            "event_time": round(t, 4),
                            "event": "explode",
                            "pump_number": pumps,
                            "threshold": thresh,
                            "gain": "",
                            "reward_params": f"{base_gain},{gain_step},{max_gain}",
                            "temp_points": temp_points,
                            "total_points": total_points,
                        })

                        feedback.text = "BOOM!"
                        feedback.draw()
                        win.flip()
                        core.wait(FIX_FEEDBACK_DUR)
                        break

                    else:
                        gain = gain_for_pump(pumps, base_gain, gain_step, max_gain)
                        temp_points += gain

                        balloon.radius = BALLOON_START_RADIUS + pumps * BALLOON_RADIUS_STEP

                        knot.pos = (0, balloon.pos[1] - balloon.radius - 0.02)
                        string.start = (0, knot.pos[1] - 0.02)
                        string.end   = (0, knot.pos[1] - 0.25)

                        rows.append({
                            "participant": info["participant"],
                            "session": info["session"],
                            "balloon": b,
                            "balloon_type": btype,
                            "event_time": round(t, 4),
                            "event": "pump",
                            "pump_number": pumps,
                            "threshold": thresh,
                            "gain": gain,
                            "reward_params": f"{base_gain},{gain_step},{max_gain}",
                            "temp_points": temp_points,
                            "total_points": total_points,
                        })

                #Collect
                if ("return" in keys) or ("enter" in keys):
                    total_points += temp_points

                    rows.append({
                        "participant": info["participant"],
                        "session": info["session"],
                        "balloon": b,
                        "balloon_type": btype,
                        "event_time": round(t, 4),
                        "event": "collect",
                        "pump_number": pumps,
                        "threshold": thresh,
                        "gain": "",
                        "reward_params": f"{base_gain},{gain_step},{max_gain}",
                        "temp_points": temp_points,
                        "total_points": total_points,
                    })

                    feedback.text = "Collected!"
                    feedback.draw()
                    win.flip()
                    core.wait(FIX_FEEDBACK_DUR)
                    break

            win.flip()
            core.wait(ITI)

        #End
        end_msg = visual.TextStim(
            win,
            text="Done!\n\nYou earned %d points!\n\nPress SPACE to exit." % total_points,
            height=0.07,
            color="white",
            wrapWidth=1.6
        )
        end_msg.draw()
        win.flip()
        event.waitKeys(keyList=["space", QUIT_KEY])

    except KeyboardInterrupt:
        pass

    # Save data
    out_dir = ensure_data_folder()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, "BART_%s_sess%s_%s.csv" % (info["participant"], info["session"], ts))
    save_rows_to_csv(rows, out_path)

    print("CWD:", os.getcwd())
    print("Saved data to:", os.path.abspath(out_path))

    win.close()
    core.quit()


if __name__ == "__main__":
    main()