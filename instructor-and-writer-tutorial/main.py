import asyncio
import csv
import json
import os
from typing import Annotated, Type, Iterable, List

import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, AfterValidator, Field
from writerai import Writer, AsyncWriter

load_dotenv()

writer_client = Writer()
async_writer_client = AsyncWriter()

# Structure of entities stored in files
class UserExtract(BaseModel):

    @staticmethod
    def first_last_name_validator(v):
        if v[0] != v[0].upper() or v[1:] != v[1:].lower() or not v.isalpha():
            raise ValueError("Name must contain only letters and stars from uppercase letter")
        return v

    first_name: Annotated[str, AfterValidator(first_last_name_validator)] = Field(
        ..., description="The name of the user"
    )
    last_name: Annotated[str, AfterValidator(first_last_name_validator)] = Field(
        ..., description="The surname of the user"
    )
    email: str

# Top level function
async def handle_file(file_path: str, response_model: Type[BaseModel], output_path: str = None) -> None:
    extension = os.path.splitext(file_path)[1]
    name = os.path.splitext(os.path.basename(file_path))[0]

    file_text = await fetch_file_text(file_path, name, extension)
    repaired_entities = await repair_data(file_text, response_model)

    print(f"Number of entities extracted from {name}{extension}: {len(repaired_entities)}")
    return generate_csv(repaired_entities, response_model, output_path)


async def fetch_file_text(file_path: str, name: str, extension: str) -> str:
    # Verifying that extension is supported
    allowed_extensions = [".txt", ".csv", ".pdf"]
    if extension not in allowed_extensions:
        raise ValueError(f"File extension {extension} is not allowed. Only {', '.join(allowed_extensions)}")

    print(f"Reading {name}{extension} content...")
    # Opening and reading the file contents
    with open(file_path, 'rb') as file:
        file_contents = file.read()

    return await parse_file(file_contents, name, extension)

async def parse_file(file_bytes_content: bytes, name: str, extension: str) -> str:
    file_text = ""

    if extension == ".pdf":
        print(f"Uploading {name}{extension} content to writer servers...")
        # Uploading the file to Writer storage using the Writer API
        file = await async_writer_client.files.upload(
            content=file_bytes_content,
            content_disposition=f"attachment; filename={name + extension}",
            content_type="application/octet-stream",
        )

        # Fetching file text using the Writer API
        print(f"Converting {name}{extension} content from PDF to text featuring writer tools...")
        file_text = await async_writer_client.tools.parse_pdf(
            file_id=file.id,
            format="text",
        )

        # Deleting the file from Writer storage using the Writer API
        print(f"Deleting {name}{extension} from writer servers...")
        await async_writer_client.files.delete(file.id)

    else:
        print(f"Converting {name}{extension} content featuring python...")
        file_text = file_bytes_content.decode("utf-8")

    return file_text

async def repair_data(file_text: str, response_model: Type[BaseModel]) -> List[BaseModel]:
    instructor_client = instructor.from_writer(client=async_writer_client)

    # Verifying that response model us BaseModel subclass
    if not issubclass(response_model, BaseModel):
        raise ValueError("Response model must be subclass of pydantic BaseModel")

    print("Extracting data featuring Instructor tools...")
    # Performing repairment featuring Instructor tools
    return await instructor_client.chat.completions.create(
        model="palmyra-x-004",
        response_model=Iterable[response_model],
        max_retries=5,
        messages=[
            {"role": "user", "content": f"Exact entities from {file_text}"},
        ],
    )

def generate_csv(entities: List[BaseModel], response_model: Type[BaseModel], output_path: str = None) -> None:
    fieldnames = list(response_model.model_json_schema()["properties"].keys())
    file_path = f"{response_model.__name__}.csv"

    if output_path:
        file_path = output_path + file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        dict_writer = csv.DictWriter(file, fieldnames=fieldnames)
        dict_writer.writeheader()
        for entity in entities:
            dict_writer.writerow(json.loads(response_model(**entity.model_dump()).model_dump_json()))

# Function for handling multiple files asynchronously
async def main():

    # Input args
    data = [
        ("example_data/ExampleFileTextFormat.txt", UserExtract, None),
        ("example_data/ExampleFilePDFFormat.pdf", UserExtract, "out/"),
    ]
    tasks = []

    # Creating tasks
    for row in data:
        tasks.append(handle_file(row[0], row[1], row[2]))

    await asyncio.gather(*tasks)


asyncio.run(main())
