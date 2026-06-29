# 🛠 Exercici de Refactorització — Backend RealWorld

## Objectiu

Aplicar els tres pilars de la refactorització sobre el codi font d'un backend
RealWorld (Flask + Couchbase). **No podeu modificar el comportament extern**:
les rutes, els endpoints i els tipus de resposta han de continuar iguals.

---

## Objectius de la refactorització

### 1. Eliminar la duplicació (DRY)

Localitzeu i unifiqueu el codi repetit:

- **Validacions**: cada `*Request` de `validation/` repeteix el mateix
  `model_validator`. Extraieu-lo a una classe base.
- **`ErrorResponse`**: apareix definit a `common.py` i a `auth.py`.
- **Consulta i extracció d'1 document**: el patró
  `for row in cursor.rows(): article = row[...]; break` es repeteix a
  `routes/v1/articles.py` i `routes/v1/profiles.py`.
- **Creació d'`Author`**: `create_article` i `create_comment` creen un
  `Author` amb els mateixos valors per defecte (`following=False`, `bio=""`,
  `image=""`).
- **`User.get_by_*`**: els tres mètodes (`get_by_username`, `get_by_email`,
  `get_user_by_id`) tenen la mateixa estructura. Unifiqueu-los.

### 2. Millorar la llegibilitat

Substituïu noms críptics, comentaris incomplets, errors tipogràfics i
incoherències:

- `final_test` → alguna cosa amb sentit
- `required_article` → `article` (o `existing_article`)
- `article` usat com a `list` a `get_articles` i com a `dict` al `for`
- `data` com a nom genèric a `update_article`, `favorite_article`, etc.
- `"PUSH"` / `"POP"` → constants amb nom (`FAVORITE_ACTION_ADD`,
  `FAVORITE_ACTION_REMOVE`)
- `meerrorssage` → `message`
- `succesfully` / `sucessfully` → `successfully`
- `register_response` usat per a login → `LoginResponse`
- Comentaris incomplets: `# Get request data of ` (no acaba)
- Trailing whitespace i espais sobrants

### 3. Reduir la complexitat

Dividiu funcions llargues en blocs més petits i especialitzats:

- **`get_articles()`** (línies 69-110): 4 branques de consulta → extraieu
  un `_build_articles_query(author, favorited, tag, skip, limit)`.
- **`follow_unfollow()`** (línies 25-89): lògica de FOLLOW i UNFOLLOW
  mesclada → separeu en `_handle_follow(...)` i `_handle_unfollow(...)`.
- **`favorite_article()`** (línies 138-172): barreja localització de
  l'article, decisió d'acció i actualització.
- **`User.get_by_username / get_by_email / get_user_by_id`**: un sol mètode
  `_query_user(field, value)`.

---

## Estructura del codi inicial

```
backend-refactor/
  realworld/
    models/
      articles.py      # Author, Article
      comments.py      # Author, Comment (Author duplicat!)
      profiles.py      # Profiles
      users.py         # User amb 3 getters quasi-idèntics
    routes/v1/
      articles.py      # get_articles() massa llarg, favorite_article()
                       # amb noms confusos, duplicació de patró DB
      comments.py      # create_comment duplica Author
      profiles.py      # follow_unfollow() 89 línies, lògica barrejada
      users.py         # create_user, login_user, get_current_user
    validation/
      articles.py      # model_validator repetit
      auth.py          # model_validator repetit + ErrorResponse duplicat
      comments.py      # model_validator repetit
      common.py        # ErrorResponse
      profiles.py      # sense model_validator (inconsistent!)
```

---

## Lliurament

Lliureu el codi refactoritzat dins de `solucion/` amb la mateixa estructura
de directoris. **Documenteu breument** (al capçal de cada fitxer o en un
`solucion/README.md`) quins canvis heu fet i per a quin objectiu.

Podeu treballar individualment o en parelles.
