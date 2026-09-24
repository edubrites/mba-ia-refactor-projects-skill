from models.category import Category
from models.errors import NotFoundError
from models.task import Task
from models.validators import validate_category


class CategoryController:
    def list_categories(self):
        task_counts = Task.counts_per_category()
        result = []
        for category in Category.list_all():
            data = category.to_dict()
            data['task_count'] = task_counts.get(category.id, 0)
            result.append(data)
        return result, 200

    def create_category(self, data):
        category = Category(**validate_category(data))
        category.save()
        return category.to_dict(), 201

    def update_category(self, cat_id, data):
        category = self._get_or_404(cat_id)
        for name, value in validate_category(data, partial=True).items():
            setattr(category, name, value)
        category.save()
        return category.to_dict(), 200

    def delete_category(self, cat_id):
        category = self._get_or_404(cat_id)
        category.delete()
        return {'message': 'Categoria deletada'}, 200

    @staticmethod
    def _get_or_404(cat_id):
        category = Category.get(cat_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        return category
