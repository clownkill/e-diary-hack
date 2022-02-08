import argparse
import os
import random
import sys

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

django.setup()
from datacenter.models import Schoolkid, Lesson, Commendation, Chastisement, Mark


def fetch_schoolkid(child_name):
	try:
		child = Schoolkid.objects.get(full_name__contains=child_name)
	except django.core.exceptions.MultipleObjectsReturned:
		print('Слишком много учеников с указанным именем. Пожалуйста уточните имя.')
		sys.exit()
	except django.core.exceptions.ObjectDoesNotExist:
		print('Ученик с таким именем отсутствует. Пожалуйста уточните имя.')
		sys.exit()
	return child


def fix_marks(child):
	negative_marks = Mark.objects.filter(schoolkid=child, points__lte=3)
	for mark in negative_marks:
		target_mark = Mark.objects.get(pk=mark.pk)
		target_mark.points = 5
		target_mark.save()


def create_commendation(child, subject_title):
	commendations = [
		'Молодец!',
		 'Отлично!',
		 'Хорошо!',
		 'Гораздо лучше, чем я ожидал!',
		 'Ты меня приятно удивил!'
	]
	year = child.year_of_study
	letter = child.group_letter
	lessons = Lesson.objects.filter(year_of_study=year, group_letter=letter)
	target_lessons = lessons.filter(subject__title=subject_title)
	last_lesson = target_lessons.order_by('-date').first()
	Commendation.objects.create(
		text=random.choice(commendations),
		created=last_lesson.date,
		schoolkid=child,
		subject=last_lesson.subject,
		teacher=last_lesson.teacher
	)


def remove_chastisements(child):
	chastisement = Chastisement.objects.filter(schoolkid=child)
	chastisement.delete()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-ln', '--last_name', help='Фамилия ученика', default='Фролов')
	parser.add_argument('-fn', '--first_name', help='Имя ученика', default='Иван')
	parser.add_argument('-p', '--patronymic', help='Отчетсво ученика', default='')
	parser.add_argument('-s', '--subject', help='Название предмета', default='Математика')
	args = parser.parse_args()
	kid_full_name = f'{args.last_name} {args.first_name} {args.patronymic}'
	schoolkid = fetch_schoolkid(kid_full_name)
	print('Начинаю исправлять оценки')
	fix_marks(schoolkid)
	print('Оценки исправлены')
	print('Начинаю удалять замечания')
	remove_chastisements(schoolkid)
	print('Замечания удалены')
	print('Начинаю добавлять похвалу')
	try:
		create_commendation(schoolkid, args.subject)
	except AttributeError:
		print('Неправильно введено название предмета. Пожалуйста выберети правильный предмет из расписания.')
		sys.exit()
	print('Похвала добавлена')