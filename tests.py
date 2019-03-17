import unittest
from app import *
from models import *
from uuid import uuid4


class TestUsersModel(unittest.TestCase):
    # Generate unique email for user
    ident = uuid4()
    # Insert user to DB
    user = Users(email=ident, password='qwerty01258#$%^&*', name='testing',
                 surname='sur_testing', phone='+791158725350')
    db.session.add(user)
    db.session.commit()

    def test_insert_user(self):
        # Get User with such email from DB
        get_user = Users.query.filter(Users.email == str(self.ident)).first()
        # Assert fields
        self.assertEqual(self.user.email, get_user.email)
        self.assertEqual(self.user.password, get_user.password)
        self.assertEqual(self.user.name, get_user.name)
        self.assertEqual(self.user.surname, get_user.surname)
        self.assertEqual(self.user.phone, get_user.phone)

    def test_email_selection(self):
        user = Users.query.filter(self.user.email == Users.email).all()
        a = 0
        for use in user:
            a = a+1
        self.assertEqual(a, 1)

    def test_insert_fail(self):
        user_exist = Users.query.filter(Users.email == self.user.email).first()
        # If there's such user in DB
        if not user_exist:
            self.assertTrue(1 == 0)
        else:
            self.assertTrue(1 == 1)


class TestMenuModel(unittest.TestCase):
        # Insert menu_item to DB
        item = Menu(category_id=2, name="Блюдо", price=1000, desc_short="asd", desc_long="asdasd",
                    weight=100, recommended=True, delivery=False)
        db.session.add(item)
        db.session.commit()

        def test_item_results(self):
            dict_item = self.item.prepare_json()
            select = Menu.query.filter(self.item.item_id == Menu.item_id).first()
            dict_select = select.prepare_json()
            self.assertDictEqual(dict_item, dict_select)

        def test_load_image(self):
            err = self.item.load_image()
            self.assertEqual(err, 'NOT OK')

        def test_del_image(self):
            code = self.item.delete_image()
            self.assertEqual(code, None)


if __name__ == '__main__':
    unittest.main()
