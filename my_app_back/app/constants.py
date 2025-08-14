from app.enum import ExerciseEnum, ExerciseMeasureEnum, ExerciseRatingEnum

MAPPING_EXERCISE_TO_EXERCISE_MEASURES = {
    ExerciseEnum.SQUAT: [
        ExerciseMeasureEnum.SQUAT_TORSO_ANGLE,
        ExerciseMeasureEnum.HEAD_ALIGNMENT,
        ExerciseMeasureEnum.SQUAT_DEPTH,
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
    }
}
