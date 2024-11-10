import uuid

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

DbMetadata = MetaData()
DbOrm = declarative_base(metadata=DbMetadata)


class StoredFileOrm(DbOrm):
    __tablename__ = 'stored_files'

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    mime: Mapped[str] = mapped_column(sa.String(), nullable=False)
    file_name: Mapped[str] = mapped_column(sa.String(), nullable=False)
    contents: Mapped[bytes] = mapped_column(sa.LargeBinary(), nullable=False)
    topic: Mapped[str] = mapped_column(sa.String(), nullable=True, default=None)


class StoredFilePart(DbOrm):
    __tablename__ = 'stored_file_entry'

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    file_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('stored_files.id'))
    page: Mapped[int] = mapped_column(sa.Integer(), nullable=False)
    text: Mapped[str] = mapped_column(sa.String(), nullable=False)
    text_enrich: Mapped[str] = mapped_column(sa.String(), nullable=True, default=None)
    vector: Mapped[bytes] = mapped_column(sa.LargeBinary(), nullable=True, default=None)

