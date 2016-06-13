# GoTags

GoTags is a Sublime Text plugin to append or remove tags for Golang struct.

Functionality includes:

- Append JSON tag with snake cased field name or remove JSON tag
- Append XML tag with snake cased field name or remove XML tag
- Append Xorm tag with xorm field type or remove Xorm tag

## Usage

By default via the keyboard shortcut: `Super + Shift + G`, `Super + Shift + T`
on OSX or `Ctrl + Shift + G`, `Ctrl + Shift + T` on other platforms(or change it
in ${packages}/User/Default (plantform).sublime-keymap). Then choice the action
you want.

** Makesure lines `type STRUCT_NAME struct{` are in select region. **

For example:

```go
type Example struct {
    FieldOne int       ``         // int field
    FieldTwo string    `orig tag` // string field
    FieldThree time.Time // time field
}
```

Then select `type Example struct {` line (or this is current line) and type the
shortcut, select action `JSON: Append tags`:

```go
type Example struct {
	FieldOne	int	`json:"field_one"`         // int field
	FieldTwo	string	`orig tag json:"field_two"` // string field
	FieldThree	time.Time	`json:"field_three"` // time field
}
```

After save with gofmt:

```go
type Example struct {
	FieldOne   int       `json:"field_one"`          // int field
	FieldTwo   string    `orig tag json:"field_two"` // string field
	FieldThree time.Time `json:"field_three"`        // time field
}
```

## Idea from:

[gotag](https://github.com/suifengRock/gotag): golang auto generate struct tag.
