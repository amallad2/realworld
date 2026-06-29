# Solució — Exercici de Refactorització

## Canvis aplicats

### 1. Eliminar duplicació (DRY)

| Fitxer | Què s'ha fet |
|---|---|
| `validation/base.py` | Nova classe `ValidatedModel` amb el `model_validator` comú. |
| `validation/auth.py` | Eliminat `ErrorResponse` duplicat; s'importa des de `common.py`. Totes les classes amb validació hereten de `ValidatedModel`. |
| `validation/articles.py` | Idem: `CreateArticleRequest`, `UpdateArticleRequest`, `DeleteArticleRequest`, `FavoriteArticleRequest` hereten de `ValidatedModel`. |
| `validation/comments.py` | `CreateCommentRequest` hereta de `ValidatedModel`. |
| `models/users.py` | Els tres mètodes `get_by_username`, `get_by_email`, `get_user_by_id` deleguen en un sol mètode `_query_user(field, value)`. |
| `models/comments.py` | Eliminada classe `Author` duplicada; s'importa des de `models/articles.py`. |
| `routes/v1/articles.py` | Extracció de `_fetch_article_by_id()`, `_fetch_article_by_id_and_author()`, `_rows_to_list()` per eliminar el patró repetit `for row in ...`. |
| `routes/v1/profiles.py` | Extracció de `_fetch_user_by_username()`, `_fetch_profile()` per eliminar consultes duplicades. |

### 2. Millorar llegibilitat

| Fitxer | Què s'ha fet |
|---|---|
| `routes/v1/articles.py` | `final_test` → `result_message`; `required_article` → `article`; `"PUSH"/"POP"` → constants `FAVORITE_ACTION_ADD`, `FAVORITE_ACTION_REMOVE`; `meerrorssage` → `message`; `sucessfully` → `successfully`. |
| `routes/v1/profiles.py` | `succesfully` → `successfully`; `usr` → `user`; noms de variables més clars. |
| `routes/v1/users.py` | `register_response` usat per a login → `response_data`; extracció de `_build_user_response()`. |
| Tots | Trailing whitespace eliminat; espais sobrants corregits. |

### 3. Reduir complexitat

| Fitxer | Què s'ha fet |
|---|---|
| `routes/v1/articles.py` | `get_articles()`: les 4 branques s'extreuen a `_build_articles_query()`. |
| `routes/v1/profiles.py` | `follow_unfollow()` dividida en `_handle_follow()`, `_handle_unfollow()`, `_fetch_user_by_username()`, `_fetch_profile()`. Reducció de 89 → ~20 línies la funció principal. |
| `routes/v1/articles.py` | `favorite_article()` simplificada usant `article.get("favorited")` i `in` operator per decidir l'acció. |
| `routes/v1/comments.py` | `create_comment()`: separada validació d'article de la creació del comentari. |
