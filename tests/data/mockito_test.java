// -*- coding: utf-8 -*-
// j2 from 'macros.j2' import header
// %% [markdown] lang="de" tags=["slide"]
// {{ header("Mocking mit Mockito", "Mocking with Mockito") }}

// %% [markdown] lang="de" tags=["subslide"]
//
// # Das Mockito Mocking Framework
//
// - [Mockito](https://site.mockito.org) ist ein Mocking-Framework für Java
// - Ermöglicht das Erstellen von Mock-Objekten

// %% [markdown] lang="en" tags=["subslide"]
//
// # The Mockito Mocking Framework
//
// - [Mockito](https://site.mockito.org) is a mocking framework for Java
// - Allows the creation of mock objects


// %% tags=["keep", "subslide"]
// %maven org.junit.jupiter:junit-jupiter-api:5.8.2
// %maven org.junit.jupiter:junit-jupiter-engine:5.8.2
// %maven org.junit.platform:junit-platform-launcher:1.9.3
// %maven org.mockito:mockito-core:4.11.+

// %% tags=["subslide", "keep"]
// %jars .
// %classpath testrunner-0.1.jar

// %% tags=["keep"]
import static testrunner.TestRunner.runTests;

// %% [markdown] lang="de" tags=["subslide"]
//
// ## Beispiel: Mocken einer Liste
//
// - Erstellen eines Mock-Objekts für eine Liste
// - Implementiert alle Methoden des `List`-Interfaces
// - Kann verwendet werden, um Methodenaufrufe zu überprüfen

// %% [markdown] lang="en" tags=["subslide"]
//
// ## Example: Mocking a List
//
// - Creating a mock object for a list
// - Implements all methods of the `List` interface
// - Can be used to verify method calls

// %% tags=["keep"]
import java.util.List;

// %% tags=["keep"]
import static org.mockito.Mockito.*;

// %%
List mockedList = mock(List.class);

// %%
mockedList.add("Hello!");

// %% tags=["subslide", "keep"]
class TestMockedList {
    @Test
    void testHelloInList() {
        List mockedList = mock(List.class);
        mockedList.add("Hello!");

        verify(mockedList).add("Hello!");
    }
}

