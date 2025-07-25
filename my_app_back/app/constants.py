from app.enum import ExerciseEnum, ExerciseMeasureEnum

MAPPING_EXERCISE_TO_EXERCISE_MEASURE = {
    ExerciseEnum.SQUAT: [
        ExerciseMeasureEnum.SQUAT_KNEE_ALIGNMENT,
        ExerciseMeasureEnum.SQUAT_DEPTH,
        ExerciseMeasureEnum.SQUAT_TORSO_ANGLE,
        ExerciseMeasureEnum.HEAD_ALIGNMENT,
    ],
}
