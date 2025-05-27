# API de gestion de bibliotheque 

Ce projet est une application de gestion de bibliothèque universitaire basée sur **FastAPI**, structurée selon une architecture **N-Tiers**. Elle expose une API RESTful organisée pour gérer les livres, les utilisateurs et les emprunts.

# Implémentation de la couche de présentation avec FastAPI

## Exercice 1 : Définition des schémas Pydantic  

Les **schémas Pydantic** servent à valider et structurer les données entrantes et sortantes de l'API. Ils assurent que les données respectent des contraintes de type, longueur, format...  
Chaque entité (Book, User, Loan, Token) possède un fichier dédié dans **src/api/schemas/**  

### 📖 Schémas liés aux livres - src/api/schemas/books.py   

**`BookBase` :**  ce schéma définit les champs de base d’un livre : title, author, isbn, publication_year, description, quantity (type, longueur min/max, description, obligatoire/optionnel). Il est utilisé comme base pour les autres schémas livres.

**`BookCreate` :** ce schéma hérite de BookBase, on l'utilise pour la création d’un livre :   
```python
# Exemple : BookCreate
class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: int
    quantity: int
```  

Il peut recevoir un objet JSON comme celui-ci depuis le frontend :

```json
{
  "title": "1984",
  "author": "George Orwell",
  "isbn": "9780451524935",
  "quantity": 3
}
```

**`BookUpdate` :** ce schéma contient les mêmes champs que BookBase, mais tous sont optionnels. On l'utilise pour mettre à jour un livre partiellement - PATCH (ex: si on n'a qu'un seul champs à mettre à jour on n'a pas besoin de resaisir toutes les informations).  

**`BookInDBBase` :** ce schéma hérite de BookBase et ajoute les champs id, created_at, updated_at. Il sert de base aux objets renvoyés par l'API.   

**`Book` :** ce schéma est un alias de BookInDBBase, il est utilisé dans les réponses API.

---
### 🧑🏼‍🎓 Schémas liés aux utilisateurs - src/api/schemas/users.py 

**`UserBase` :** ce schéma définit les champs de base d’un utilisateur : email, full_name, is_active, is_admin (type, longueur min/max, description, obligatoire/optionnel). Il est utilisé comme base pour les autres schémas utilisateurs.  

**`UserCreate` :** ce schéma hérite de UserBase et ajoute un champ password, on l'utilise pour la création d’un compte utilisateur.  
```python
# Exemple : UserCreate
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
```  
Exemple JSON :  

```json
{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "Password123"
}
``` 

**`UserUpdate` :** ce schéma contient les mêmes champs que UserCreate, mais tous sont optionnels. On l'utilise pour mettre à jour un utilisateur partiellement.  

**`UserInDBBase` :**	ce schéma hérite de UserBase et ajoute les champs id, created_at, updated_at. Il est utilisé comme base pour les réponses API.  

**`User` :**	ce schéma est un alias de UserInDBBase, il est utilisé dans les réponses API.  

**`UserWithPassword` :**	ce schéma est une variante de UserInDBBase qui inclut un hashed_password. On l'utilise pour la gestion de l’authentification.  

---
### 📆 Schémas liés aux emprunts  - src/api/schemas/loans.py

**`LoanBase` :**	ce schéma définit les champs de bases d'un emprunt : user_id, book_id, loan_date, due_date, return_date (type, longueur min/max, description, obligatoire/optionnel). Il est utilisé comme base pour les autres schémas emprunts.   

**`LoanCreate` :** ce schéma hérite de LoanBase, on l'utilise pour la création d'un nouvel emprunt.  
```python
# Exemple : LoanCreate
class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    due_date: date
```  
Exemple JSON : 

```json
{
  "user_id": 1,
  "book_id": 42,
  "due_date": "2025-06-15"
}
```

**`LoanUpdate` :** ce schéma est utilisé pour mettre à jour la date de retour du livre ou la date d’échéance de l'emprunt.  

**`LoanInDBBase` :**	ce schéma hérite de LoanBase et ajoute les champs id, created_at, updated_at. Il est utilisé comme base pour les réponses API.    

**`Loan` :**	ce schéma est un alias de LoanInDBBase, il est utilisé dans les réponses API.  

---
### 🔐 Schémas pour l’authentification - src/api/schemas/token.py
  
**`Token` :**	ce schéma contient le access_token (JWT) et son type (bearer).  

**`TokenPayload` :**	ce schéma représente les données contenues dans le token JWT : identifiant de l’utilisateur (sub).  

---
### 🔃 Importation des schémas - src/api/schemas/__init__.py   

Ce fichier permet de faciliter les imports dans les autres modules du projet, comme les routes :  
``` python
from .books import Book, BookCreate, BookUpdate
from .users import User, UserCreate, UserUpdate
from .loans import Loan, LoanCreate, LoanUpdate
from .token import Token, TokenPayload
```
---
### Conclusion  

Ce système permet de garantir la cohérence des données échangées entre le client, la base de données et les routes FastAPI.  

## Exercice 2 : Implémentation des routes API  

Cet exercice consiste à créer les routes HTTP REST permettant d’interagir avec les entités principales (books, users, loans, authentification) via l’API. Chaque entité possède son fichier de routes dans **src/api/routes/**  

### 📚 Routes pour les livres - src/api/routes/books.py  

Fonctionnalités :
- Récupérer la liste des livres (GET)
- Créer un nouveau livre (POST)
- Récupérer un livre par son ID (GET)
- Mettre à jour un livre (PUT)
- Supprimer un livre (DELETE)  
  
Exemple pour créer un nouveau livre :    
```python
@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    db: Session = Depends(get_db),
    book_in: BookCreate
) -> Any:
    repository = BookRepository(BookModel, db)
    book = repository.create(obj_in=book_in)
    return book
```
---
### 👥 Routes pour les utilisateurs - src/api/routes/users.py  

Fonctionnalités : 
- Récupérer la liste des utilisateurs (GET)
- Créer un nouvel utilisateur (POST)
- Récupérer un utilisateur par son ID (GET)
- Mettre à jour un utilisateur (PUT)
- Supprimer un utilisateur (DELETE)  
  
Exemple pour créer un nouvel utilisateur avec vérification d’e-mail existant et hashage du mot de passe :  
```python
@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    repository = UserRepository(UserModel, db)
    if repository.get_by_email(email=user_in.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.dict()
    user_data["hashed_password"] = hashed_password
    del user_data["password"]
    return repository.create(obj_in=user_data)
```  
---
### 📆 Routes pour les emprunts - src/api/routes/loans.py  

Fonctionnalités :  
- Récupérer la liste des emprunts (GET)
- Créer un nouvel emprunt (POST)
- Récupérer un emprunt par son ID (GET)
- Mettre à jour un emprunt (PUT)
- Supprimer un emprunt (DELETE)  

```python
@router.post("/", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_loan(*, db: Session = Depends(get_db), loan_in: LoanCreate) -> Any:
    user = UserRepository(UserModel, db).get(id=loan_in.user_id)
    book = BookRepository(BookModel, db).get(id=loan_in.book_id)

    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")
    if not book or book.quantity <= 0:
        raise HTTPException(400, "Livre non disponible")

    if not loan_in.due_date:
        loan_data = loan_in.dict()
        loan_data["due_date"] = datetime.utcnow() + timedelta(days=14)
    else:
        loan_data = loan_in.dict()

    loan = LoanRepository(LoanModel, db).create(obj_in=loan_data)

    # Mise à jour du stock
    book.quantity -= 1
    BookRepository(BookModel, db).update(db_obj=book, obj_in={"quantity": book.quantity})

    return loan
```
---
### 🔐 Routes pour l'authentification - src/api/routes/auth.py  

Connexion via email + mot de passe, renvoie un token JWT utilisable pour les routes protégées :

```python
# Route `/auth/login`
@router.post("/login", response_model=Token)
def login_access_token(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    user = repository.get_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(subject=user.id)
    return { "access_token": token, "token_type": "bearer" }
```  
Exemple de réponse :

```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```  
---
### 🔃 Pour regrouper toutes les routes - src/api/routes/__init__.py   

Les routes sont regroupées par fonctionnalité dans des fichiers séparés puis incluses dans un routeur principal :

```python
# routes/__init__.py
api_router = APIRouter()
api_router.include_router(books_router, prefix="/books", tags=["books"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
```  

Puis dans `main.py` :

```python
app.include_router(api_router, prefix="/api/v1")
```  

Exemples d’URL disponibles :
- `/api/v1/books/`
- `/api/v1/users/`
- `/api/v1/auth/login`

# Développement de la couche métier  

La **couche métier** constitue le cœur de la logique métier de l'application. Elle fait le lien entre la **couche de présentation** (API) et la **couche d'accès aux données** (repositories). Elle encapsule toutes les règles métier, les validations spécifiques et les traitements complexes.  

## Exercice 1 : Création d'un service de base - src/services/base.py    

Le service de base fournit des fonctionnalités CRUD communes à tous les services. On utilise une classe générique **BaseService** pour tout centraliser.    

### Fonctionnalités principales :  
- Opérations CRUD génériques (Create, Read, Update, Delete) :  
```
# CREATE - Créer un nouvel objet
def create(self, *, obj_in: CreateSchemaType) -> ModelType:
    return self.repository.create(obj_in=obj_in)

# READ - Lire un objet par ID
def get(self, id: Any) -> Optional[ModelType]:
    return self.repository.get(id=id)

# UPDATE - Mettre à jour un objet existant  
def update(self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
    return self.repository.update(db_obj=db_obj, obj_in=obj_in)

# DELETE - Supprimer un objet
def remove(self, *, id: int) -> ModelType:
    return self.repository.remove(id=id)
```
- Gestion de la pagination avec une limite à 100 objets pour éviter de charger tous les enregistrements :
```
# Exemple d'utilisation : pour récupérer les livres 20 à 40 
service.get_multi(skip=20, limit=20)
```
- Utilisation du **pattern Repository** : le service délègue au repository au lieu d'accéder directement à la base de données :
```
# Le service orchestre, le repository exécute
def get(self, id: Any) -> Optional[ModelType]:
    return self.repository.get(id=id)
```
- Définition des types génériques pour la réutilisabilité avec n'importe quel type d'objet :   
```python
# Type du modèle (User, Book, Loan...)
ModelType = TypeVar("ModelType", bound=Base) 
# Schéma de création
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Schéma de mise à jour
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
```
  
### Structure du service :  
```python
class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def get(self, id: Any) -> Optional[ModelType]
    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]
    def create(self, *, obj_in: CreateSchemaType) -> ModelType
    def update(self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType
    def remove(self, *, id: int) -> ModelType
```    

### Avantages :  

- **Réutilisabilité :** toutes les opérations CRUD de base sont implémentées une seule fois ;
- **Cohérence :** on utilsie une seule et même interface pour tous les services ;
- **Maintenabilité :** les modifications sont centralisées dans un seul endroit ;
- **Type Safety :** utilisation des génériques pour éviter les erreurs de type

## Exercice 2 : Implémentation du service utilisateur - src/services/users.py  

Le service utilisateur étend le service de base avec des fonctionnalités spécifiques à la gestion des utilisateurs, comme l'authentification, la gestion des mots de passe et les vérifications de sécurité.  

###   



## Exercice 3 : Implémentation du service de livres - src/services/books.py    

Le `BookService` est une classe de service qui gère la logique métier liée aux livres dans une application. Il hérite de `BaseService` et utilise le pattern Repository pour l'accès aux données.  

### Imports et Dépendances

```python
from typing import List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
```

- **typing** : fournit les annotations de type pour améliorer la lisibilité et la validation du code
- **sqlalchemy.orm.Session** : type SQLAlchemy pour la gestion des sessions de base de données

```python
from ..repositories.books import BookRepository
from ..models.books import Book
from ..api.schemas.books import BookCreate, BookUpdate
from .base import BaseService
```

- **BookRepository** : classe repository qui gère l'accès aux données des livres
- **Book** : modèle SQLAlchemy représentant un livre en base de données
- **BookCreate, BookUpdate** : schémas Pydantic pour la création et la mise à jour des livres
- **BaseService** : classe de base qui fournit les opérations CRUD génériques

### Définition de la Classe

```python
class BookService(BaseService[Book, BookCreate, BookUpdate]):
```

La classe hérite de `BaseService` avec des paramètres génériques :
- `Book` : Le modèle de données
- `BookCreate` : Le schéma pour créer un livre
- `BookUpdate` : Le schéma pour mettre à jour un livre

### Constructeur

```python
def __init__(self, repository: BookRepository):
    super().__init__(repository)
    self.repository = repository
```

- Initialise la classe parent avec le repository
- Stocke une référence au repository pour un accès direct aux méthodes spécifiques

### Méthodes de Recherche

#### Recherche par ISBN

```python
def get_by_isbn(self, *, isbn: str) -> Optional[Book]:
    return self.repository.get_by_isbn(isbn=isbn)
```

- **Paramètre** : `isbn` (chaîne de caractères) passé en keyword-only (`*`)
- **Retour** : `Optional[Book]` - un livre ou `None` si non trouvé
- **Fonction** : Récupère un livre unique par son ISBN

#### Recherche par Titre

```python
def get_by_title(self, *, title: str) -> List[Book]:
    return self.repository.get_by_title(title=title)
```

- **Paramètre** : `title` (chaîne de caractères)
- **Retour** : `List[Book]` - liste des livres correspondants
- **Fonction** : Recherche partielle par titre (peut retourner plusieurs résultats)

#### Recherche par Auteur

```python
def get_by_author(self, *, author: str) -> List[Book]:
    return self.repository.get_by_author(author=author)
```

- **Paramètre** : `author` (chaîne de caractères)
- **Retour** : `List[Book]` - liste des livres de l'auteur
- **Fonction** : Recherche partielle par nom d'auteur

### Création de Livre

```python
def create(self, *, obj_in: BookCreate) -> Book:
    existing_book = self.get_by_isbn(isbn=obj_in.isbn)
    if existing_book:
        raise ValueError("L'ISBN est déjà utilisé")
    return self.repository.create(obj_in=obj_in)
```

**Logique métier** :
1. Vérifie si l'ISBN existe déjà dans la base
2. Lève une exception `ValueError` si l'ISBN est déjà utilisé
3. Crée le livre via le repository si l'ISBN est unique

Cette méthode surcharge la méthode `create` héritée pour ajouter la validation de l'ISBN.

### Gestion des Quantités

```python
def update_quantity(self, *, book_id: int, quantity_change: int) -> Book:
    book = self.get(id=book_id)
    if not book:
        raise ValueError(f"Livre avec l'ID {book_id} non trouvé")

    new_quantity = book.quantity + quantity_change
    if new_quantity < 0:
        raise ValueError("La quantité ne peut pas être négative")

    return self.repository.update(db_obj=book, obj_in={"quantity": new_quantity})
```

**Logique métier** :
1. Récupère le livre par ID (utilise la méthode `get` héritée)
2. Vérifie que le livre existe
3. Calcule la nouvelle quantité
4. Valide que la quantité reste positive
5. Met à jour le livre avec la nouvelle quantité

### Exemple d'utilisation

```python
# Initialisation
book_repository = BookRepository(session)
book_service = BookService(book_repository)

# Recherche
book = book_service.get_by_isbn(isbn="978-2-123456-78-9")
books_by_author = book_service.get_by_author(author="Hugo")

# Création
new_book_data = BookCreate(title="Nouveau Livre", isbn="978-2-987654-32-1", ...)
book = book_service.create(obj_in=new_book_data)

# Gestion des stocks
book_service.update_quantity(book_id=1, quantity_change=5)  # Ajoute 5 exemplaires
book_service.update_quantity(book_id=1, quantity_change=-2)  # Retire 2 exemplaires
```

Ce service encapsule toute la logique métier liée aux livres tout en déléguant l'accès aux données au repository, respectant ainsi le principe de séparation des responsabilités. 