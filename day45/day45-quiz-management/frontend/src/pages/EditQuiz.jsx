import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm, useFieldArray } from 'react-hook-form'
import { useQuery } from 'react-query'
import { toast } from 'react-hot-toast'
import { quizService } from '../services/api'
import { useQuiz } from '../context/QuizContext'
import { Plus, Trash2, Save, ArrowLeft, HelpCircle } from 'lucide-react'

const EditQuiz = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { dispatch } = useQuiz()
  const [loading, setLoading] = useState(false)

  const { data: quiz, isLoading, error } = useQuery(
    ['quiz', id],
    () => quizService.getQuiz(id)
  )

  const { register, control, handleSubmit, reset, watch, formState: { errors } } = useForm({
    defaultValues: {
      title: '',
      description: '',
      tags: '',
      questions: []
    }
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'questions'
  })

  const watchedQuestions = watch('questions')

  useEffect(() => {
    if (quiz) {
      reset({
        title: quiz.title,
        description: quiz.description,
        tags: quiz.tags ? quiz.tags.join(', ') : '',
        questions: quiz.questions.map(q => ({
          ...q,
          options: q.options || ['', '', '']
        }))
      })
    }
  }, [quiz, reset])

  const addQuestion = () => {
    append({
      text: '',
      type: 'multiple_choice',
      options: ['', '', ''],
      correct_answer: ''
    })
  }

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const quizData = {
        ...data,
        tags: data.tags ? data.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [],
        questions: data.questions.map(q => ({
          ...q,
          options: q.type === 'multiple_choice' ? q.options.filter(Boolean) : null
        }))
      }
      
      const updatedQuiz = await quizService.updateQuiz(id, quizData)
      dispatch({ type: 'UPDATE_QUIZ', payload: updatedQuiz })
      toast.success('Quiz updated successfully!')
      navigate('/dashboard')
    } catch (error) {
      toast.error('Failed to update quiz')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load quiz. Please try again.</p>
        <button
          onClick={() => navigate('/dashboard')}
          className="btn-primary mt-4"
        >
          Back to Dashboard
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-secondary flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Edit Quiz</h1>
            <p className="text-gray-600">Modify your quiz content and settings</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Quiz Basic Info */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quiz Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quiz Title *
              </label>
              <input
                {...register('title', { required: 'Quiz title is required' })}
                type="text"
                className="form-input"
                placeholder="Enter quiz title"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                {...register('description')}
                rows={3}
                className="form-input"
                placeholder="Brief description of the quiz"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tags
              </label>
              <input
                {...register('tags')}
                type="text"
                className="form-input"
                placeholder="Enter tags separated by commas"
              />
            </div>
          </div>
        </div>

        {/* Questions */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Questions</h2>
            <button
              type="button"
              onClick={addQuestion}
              className="btn-primary flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>Add Question</span>
            </button>
          </div>

          {fields.map((field, questionIndex) => (
            <div key={field.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <HelpCircle className="h-5 w-5 text-primary-600" />
                  <h3 className="text-md font-medium text-gray-900">
                    Question {questionIndex + 1}
                  </h3>
                </div>
                
                {fields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => remove(questionIndex)}
                    className="text-red-600 hover:text-red-700 p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>

              <div className="space-y-4">
                {/* Question Text */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Question Text *
                  </label>
                  <input
                    {...register(`questions.${questionIndex}.text`, {
                      required: 'Question text is required'
                    })}
                    type="text"
                    className="form-input"
                    placeholder="Enter your question"
                  />
                  {errors.questions?.[questionIndex]?.text && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.questions[questionIndex].text.message}
                    </p>
                  )}
                </div>

                {/* Question Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Question Type
                  </label>
                  <select
                    {...register(`questions.${questionIndex}.type`)}
                    className="form-input"
                  >
                    <option value="multiple_choice">Multiple Choice</option>
                    <option value="true_false">True/False</option>
                    <option value="text">Text Answer</option>
                  </select>
                </div>

                {/* Options for Multiple Choice */}
                {watchedQuestions[questionIndex]?.type === 'multiple_choice' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Answer Options
                    </label>
                    <div className="space-y-2">
                      {watchedQuestions[questionIndex]?.options?.map((_, optionIndex) => (
                        <div key={optionIndex} className="flex items-center space-x-2">
                          <input
                            {...register(`questions.${questionIndex}.options.${optionIndex}`, {
                              required: 'Option text is required'
                            })}
                            type="text"
                            className="form-input"
                            placeholder={`Option ${optionIndex + 1}`}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Correct Answer */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Correct Answer *
                  </label>
                  {watchedQuestions[questionIndex]?.type === 'true_false' ? (
                    <select
                      {...register(`questions.${questionIndex}.correct_answer`, {
                        required: 'Please select the correct answer'
                      })}
                      className="form-input"
                    >
                      <option value="">Select correct answer</option>
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                  ) : (
                    <input
                      {...register(`questions.${questionIndex}.correct_answer`, {
                        required: 'Correct answer is required'
                      })}
                      type="text"
                      className="form-input"
                      placeholder="Enter the correct answer"
                    />
                  )}
                  {errors.questions?.[questionIndex]?.correct_answer && (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.questions[questionIndex].correct_answer.message}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-end space-x-4 pt-6 border-t">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Updating...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Update Quiz</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default EditQuiz
