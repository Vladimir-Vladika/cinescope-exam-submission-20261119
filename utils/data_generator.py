from uuid import uuid4

from faker import Faker


class DataGenerator:
    def __init__(self):
        self.fake = Faker('en_US')

    def movie(self, genre_id, **overrides):
        data = {
            'name': f'AQA-{uuid4().hex}',
            'price': self.fake.random_int(min=100, max=900),
            'description': self.fake.sentence(nb_words=12),
            'imageUrl': 'https://example.com/poster.jpg',
            'location': self.fake.random_element(elements=('MSK', 'SPB')),
            'published': True,
            'genreId': genre_id,
        }
        data.update(overrides)
        return data
