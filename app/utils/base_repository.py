from typing import Type, TypeVar, Generic, List, Optional, Any

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, session: Session, id: int) -> Optional[ModelType]:
        return session.get(self.model, id)

    def get_all(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        results = session.exec(statement)
        return list(results.all())

    def create(
        self,
        session: Session,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        id: int,
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        obj_data = obj_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(
        self,
        session: Session,
        id: int
    ) -> bool:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return False
        
        session.delete(db_obj)
        session.commit()
        return True

    def count(
        self,
        session: Session
    ) -> int:
        from sqlmodel import func
        statement = select(func.count()).select_from(self.model)
        result = session.exec(statement)
        return result.one()
