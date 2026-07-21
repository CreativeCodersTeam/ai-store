# Cucumber-JVM (Java) Implementation

## Setup (Maven)

```xml
<dependencies>
  <dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-java</artifactId>
    <version>7.18.0</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-junit-platform-engine</artifactId>
    <version>7.18.0</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.junit.platform</groupId>
    <artifactId>junit-platform-suite</artifactId>
    <version>1.10.2</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

Place `.feature` files under `src/test/resources/features/` (the runner below selects
the `features` classpath resource) and glue (step) code under `src/test/java/`.

## Runner (JUnit Platform Suite)

```java
import org.junit.platform.suite.api.*;
import static io.cucumber.junit.platform.engine.Constants.*;

@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "com.example.steps")
public class RunCucumberTest {}
```

## Step Definitions (glue)

```java
import io.cucumber.java.en.*;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class CheckoutSteps {
    private final Cart cart = new Cart();

    @Given("the cart contains a {string}")
    public void cartContains(String item) { cart.add(item); }

    @When("the user checks out")
    public void checkout() { cart.checkout(); }

    @Then("the order total is {int}")
    public void orderTotal(int total) { assertEquals(total, cart.total()); }
}
```

## Hooks

```java
import io.cucumber.java.*;

public class Hooks {
    @Before public void before() { /* arrange */ }
    @After  public void after()  { /* cleanup */ }
}
```

## Run

```bash
mvn test
# Filter by tag:
mvn test -Dcucumber.filter.tags="@smoke"
```
Expected: surefire reports each scenario as a passing test.
