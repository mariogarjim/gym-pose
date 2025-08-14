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
}
