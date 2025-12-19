# Balloon Analogue Risk Task (BART) — Safe vs Risky Balloon Types

## Overview

This project implements a simplified **Balloon Analogue Risk Task (BART)** in **PsychoPy** to measure risk-taking behavior.
Participants pump a balloon to gain points, but the balloon may explode at an unknown time, causing the points for that balloon to be lost.

A creative feature of this implementation is a **visible balloon-type manipulation**:

* **Green balloons (“safe”)**: less likely to explode, but points grow more slowly
* **Red balloons (“risky”)**: more likely to explode, but points grow faster

This allows a basic experimental manipulation of how people adapt their pumping strategy under different risk or reward cues.



## Task Instructions for participants

* Press **SPACE** to pump the balloon, each pump increases points for the current balloon.
* Press **ENTER** to **COLLECT** and bank the current balloon points into the final score.
* The balloon may explode at an unknown time.
  If it explodes before collecting, all points for that balloon are lost.
* Press **ESC** at anytime to quit the experiment.



## How to Run

### Run from PsychoPy (recommended)

1. Open **PsychoPy**.
2. Open the script file (e.g., `bart_balloontypes.py`).
3. Click **Run**.
4. A dialog box will ask for `participant` and `session`.



## Dependencies

* **Python**
* **PsychoPy**

Other libraries used (included with Python):

* `random`, `os`, `csv`, `datetime`



## File Output / Where is my data saved?

After the task ends (or you quit with ESC), the script automatically creates a folder:

```
data/
```

Inside it, a CSV file will be saved with a timestamped name like:

```
BART_P001_sess001_20251218_221530.csv
```

The script prints the save path in the PsychoPy Output window:

* `CWD: ...`
* `Saved data to: ...`

So if you can’t find it, scroll to the end of the Output and copy the printed path.



## Data Format

Each row is one event (pump / collect / explode). Main columns:

* `participant`, `session`
* `balloon` (balloon index, 1–N_BALLOONS)
* `balloon_type` (`safe` or `risky`)
* `event` (`pump`, `collect`, `explode`)
* `event_time` (time in seconds since task start)
* `pump_number`
* `threshold` (explosion threshold for that balloon; hidden from participant)
* `gain` (points gained on that pump, only for pump events)
* `reward_params` (base_gain, gain_step, max_gain)
* `temp_points` (points accumulated for the current balloon at that moment)
* `total_points` (banked score after collects)



## Experimental Design Notes

* Balloon types are randomly assigned:

  * `P_SAFE = 0.5` (50% safe, 50% risky)
* Explosion thresholds differ by type:

  * Safe: `SAFE_THRESH_MIN..SAFE_THRESH_MAX`
  * Risky: `RISKY_THRESH_MIN..RISKY_THRESH_MAX`
* Reward growth differs by type:

  * Safe grows slower, Risky grows faster



## Examples of what can be report from the results

This script does not automatically compute statistics, but you can summarize results from the CSV such as:

* Total final score
* Average number of pumps before collecting for safe vs risky balloons
* Explosion rate for safe vs risky balloons
* Mean points collected per balloon type
