from app.enum import ExerciseEnum, ExerciseMeasureEnum

MAPPING_EXERCISE_TO_EXERCISE_MEASURE = {
    ExerciseEnum.SQUAT: [
        ExerciseMeasureEnum.SQUAT_TORSO_ANGLE,
        ExerciseMeasureEnum.SQUAT_DEPTH,
        ExerciseMeasureEnum.HEAD_ALIGNMENT,
    ],
}
