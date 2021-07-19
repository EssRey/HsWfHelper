function Person(name, age, eyeColor) {
    this.name = name;
    this.age = age;
    this.eyeColor = eyeColor;
    this.updateAge = function() {
        this.age = ++this.age;
    };
}

let person01 = new Person('Philip', 26, 'Brown');

console.log(person01);
person01.updateAge;
console.log(person01.age);