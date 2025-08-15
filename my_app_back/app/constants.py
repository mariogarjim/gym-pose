from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExerciseRatingEnum

MAPPING_EXERCISE_TO_EXERCISE_MEASURES = {
    ExerciseEnum.SQUAT: [
        ExerciseMeasureEnum.SQUAT_TORSO_ANGLE,
        ExerciseMeasureEnum.HEAD_ALIGNMENT,
        ExerciseMeasureEnum.SQUAT_DEPTH,
        ExerciseMeasureEnum.BASIC_LANDMARKS,
    ],
    ExerciseEnum.PULL_UP: [
        ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED,
        ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR,
        ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION,
        ExerciseMeasureEnum.BASIC_LANDMARKS,
    ],
    ExerciseEnum.BENCH_PRESS: [
        ExerciseMeasureEnum.BASIC_LANDMARKS,
    ],
    ExerciseEnum.SIDE_LATERAL_RAISE: [
        ExerciseMeasureEnum.BASIC_LANDMARKS,
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH,
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION,
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES,
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION,
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY,
    ],
}


MAPPING_EXERCISE_MEASURE_TO_COMMENT = {
    ExerciseEnum.SQUAT: {
        ExerciseMeasureEnum.SQUAT_DEPTH: {
            ExerciseRatingEnum.PERFECT: "The squat depth is perfect",
            ExerciseRatingEnum.WARNING: "The squat depth is not deep enough. The hips should be lower than the knees.",
        },
        ExerciseMeasureEnum.SQUAT_TORSO_ANGLE: {
            ExerciseRatingEnum.PERFECT: "The squat torso angle is perfect",
            ExerciseRatingEnum.DANGEROUS: "The squat torso angle is not correct. The torso should be perpendicular to the ground.",
        },
        ExerciseMeasureEnum.HEAD_ALIGNMENT: {
            ExerciseRatingEnum.PERFECT: "The head is aligned with the body",
            ExerciseRatingEnum.DANGEROUS: "The head is too far ahead of the body. The head should be aligned with the body.",
        },
    },
    ExerciseEnum.PULL_UP: {
        ExerciseMeasureEnum.PULL_UP_ARMS_NEARLY_EXTENDED: {
            ExerciseRatingEnum.PERFECT: "The pull up arms are nearly extended",
            ExerciseRatingEnum.WARNING: "The pull up arms are not extended enough. The arms should be fully extended.",
        },
        ExerciseMeasureEnum.PULL_UP_CHIN_OVER_BAR: {
            ExerciseRatingEnum.PERFECT: "The pull up chin is over the bar",
            ExerciseRatingEnum.WARNING: "The pull up chin is not over the bar. The chin should be over the bar.",
        },
        ExerciseMeasureEnum.PULL_UP_SHOULDER_CORRECT_POSITION: {
            ExerciseRatingEnum.PERFECT: "The shoulders are in the correct position",
            ExerciseRatingEnum.DANGEROUS: "The shoulders are not in the correct position. The shoulders should be in the correct position.",
        },
    },
    ExerciseEnum.SIDE_LATERAL_RAISE: {
        ExerciseMeasureEnum.BASIC_LANDMARKS: {
            ExerciseRatingEnum.PERFECT: "The side lateral raises are perfect",
            ExerciseRatingEnum.WARNING: "The side lateral raises are not perfect. The side lateral raises should be perfect.",
        },
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_LIFTING_TOO_HIGH: {
            ExerciseRatingEnum.PERFECT: "You don't lift your arms too high, this is good!",
            ExerciseRatingEnum.DANGEROUS: "You lift your arms too high, this is not good.",
        },
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ARMS_ABDUCTION_UP_CORRECT_POSITION: {
            ExerciseRatingEnum.PERFECT: "You lift your arms up correctly, this is good!",
            ExerciseRatingEnum.WARNING: "You don't lift your arms up enough, this is not good.",
        },
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_ELBOWS_BEND_ANGLES: {
            ExerciseRatingEnum.PERFECT: "You maintain a neutral elbow position while lifting your arms up, this is good!",
            ExerciseRatingEnum.WARNING: "You don't bend your elbows correctly. They shouldn't be bent too much neither be locked.",
        },
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION: {
            ExerciseRatingEnum.PERFECT: "You maintain a neutral shoulder position while lifting your arms up, this is good!",
            ExerciseRatingEnum.DANGEROUS: "You don't maintain a neutral shoulder position while lifting your arms up, this is not good.",
        },
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SYMMETRY: {
            ExerciseRatingEnum.PERFECT: "You maintain a symmetrical body while lifting your arms up, this is good!",
            ExerciseRatingEnum.DANGEROUS: "You don't maintain a symmetrical body while lifting your arms up, this is not good.",
        },
        ExerciseMeasureEnum.SIDE_LATERAL_RAISE_SHOULDERS_INCORRECT_ELEVATION: {
            ExerciseRatingEnum.PERFECT: "You maintain a neutral shoulder position while lifting your arms up, this is good!",
            ExerciseRatingEnum.DANGEROUS: "You don't maintain a neutral shoulder position while lifting your arms up, this is not good.",
        },
    },
    ExerciseEnum.TRICEPS_EXTENSION: {
        ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_UP_EXTENSION: {
            ExerciseRatingEnum.PERFECT: "You complete the up extension, this is good!",
            ExerciseRatingEnum.WARNING: "You don't complete the up extension, this is not good.",
        },
        ExerciseMeasureEnum.TRICEPS_EXTENSION_COMPLETE_DOWN_EXTENSION: {
            ExerciseRatingEnum.PERFECT: "You complete the down extension, this is good!",
            ExerciseRatingEnum.WARNING: "You don't complete the down extension, this is not good.",
        },
        ExerciseMeasureEnum.TRICEPS_EXTENSION_SHOULDER_ANGLE: {
            ExerciseRatingEnum.PERFECT: "You maintain a neutral shoulder angle, this is good!",
            ExerciseRatingEnum.DANGEROUS: "You don't maintain a neutral shoulder angle, your body is probably shaking during the exercise.",
        },
    },
}
